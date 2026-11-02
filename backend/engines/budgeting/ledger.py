import decimal
import math
from typing import Dict, Any
from apps.recommendations.models import HospitalScenario, ScenarioBudgetLine
from apps.trip_planning.models import TripRequest
from apps.hospitals.models import DataClassification
from integrations.exchange_rates.converter import CurrencyConverter


class BudgetLedgerEngine:
    """
    Deterministic Decimal Budget Engine for TourPlus AI.
    Calculates mandatory expenditures (Treatment, Flights, Hotel, Visa, Local Transport, Contingency)
    and computes initial discretionary budget DB_{0,s} = B_s - ME_s.
    """

    def __init__(self, reserve_percentage: decimal.Decimal = decimal.Decimal('0.05')):
        self.reserve_percentage = reserve_percentage

    def build_scenario_budget(
        self,
        scenario: HospitalScenario,
        trip_request: TripRequest
    ) -> Dict[str, Any]:
        """
        Calculates and persists all ScenarioBudgetLine items for the given scenario.
        Returns a financial ledger summary.
        """
        # Clear existing budget lines for idempotency
        ScenarioBudgetLine.objects.filter(hospital_scenario=scenario).delete()

        target_currency = str(scenario.scenario_currency or trip_request.budget_currency or 'USD')
        party_size = max(1, trip_request.party_size)
        stay_nights = max(3, trip_request.available_days)
        rooms_needed = math.ceil(party_size / 2)

        budget_lines_to_create = []

        # 1. Medical Treatment Procedure (TC_s)
        offering = scenario.hospital_treatment_offering
        cost_est = getattr(offering, 'cost_estimate', None)
        if cost_est:
            source_curr = cost_est.currency
            rate = CurrencyConverter.get_rate(source_curr, target_currency)
            t_min = CurrencyConverter.convert(cost_est.min_amount, source_curr, target_currency)
            t_exp = CurrencyConverter.convert(cost_est.expected_amount, source_curr, target_currency)
            t_max = CurrencyConverter.convert(cost_est.max_amount, source_curr, target_currency)
            data_class = cost_est.data_classification
            desc = f"Verified Medical Procedure: {offering.treatment_category.name} at {offering.hospital.name}"
        else:
            source_curr = target_currency
            rate = decimal.Decimal('1.000000')
            t_min = t_exp = t_max = decimal.Decimal('3500.00')
            data_class = DataClassification.INDICATIVE
            desc = f"Indicative Medical Procedure: {offering.treatment_category.name}"

        budget_lines_to_create.append(ScenarioBudgetLine(
            hospital_scenario=scenario,
            expense_category=ScenarioBudgetLine.ExpenseCategory.TREATMENT,
            description=desc,
            min_amount=cost_est.min_amount if cost_est else t_min,
            expected_amount=cost_est.expected_amount if cost_est else t_exp,
            max_amount=cost_est.max_amount if cost_est else t_max,
            source_currency=source_curr,
            scenario_currency=target_currency,
            exchange_rate_snapshot=rate,
            converted_expected_amount=t_exp,
            quantity=decimal.Decimal('1.00'),
            unit='procedure',
            data_classification=data_class
        ))

        # 2. International Flights (FC_s)
        # Standard indicative return flight estimate ~ $850 per traveler (min $650, max $1200)
        flight_unit_min = decimal.Decimal('650.00')
        flight_unit_exp = decimal.Decimal('850.00')
        flight_unit_max = decimal.Decimal('1200.00')
        f_min = CurrencyConverter.convert(flight_unit_min * party_size, 'USD', target_currency)
        f_exp = CurrencyConverter.convert(flight_unit_exp * party_size, 'USD', target_currency)
        f_max = CurrencyConverter.convert(flight_unit_max * party_size, 'USD', target_currency)
        flight_rate = CurrencyConverter.get_rate('USD', target_currency)

        budget_lines_to_create.append(ScenarioBudgetLine(
            hospital_scenario=scenario,
            expense_category=ScenarioBudgetLine.ExpenseCategory.INTERNATIONAL_FLIGHT,
            description=f"International Return Airfare ({party_size} traveler{'s' if party_size > 1 else ''})",
            min_amount=flight_unit_min * party_size,
            expected_amount=flight_unit_exp * party_size,
            max_amount=flight_unit_max * party_size,
            source_currency='USD',
            scenario_currency=target_currency,
            exchange_rate_snapshot=flight_rate,
            converted_expected_amount=f_exp,
            quantity=decimal.Decimal(str(party_size)),
            unit='travelers',
            data_classification=DataClassification.INDICATIVE
        ))

        # 3. Accommodation / Recovery Lodging (HC_s)
        # Nightly rate for accredited medical recovery hotel ~ $75/night (min $55, max $110)
        nightly_min = decimal.Decimal('55.00')
        nightly_exp = decimal.Decimal('75.00')
        nightly_max = decimal.Decimal('110.00')
        total_room_nights = stay_nights * rooms_needed
        h_min = CurrencyConverter.convert(nightly_min * total_room_nights, 'USD', target_currency)
        h_exp = CurrencyConverter.convert(nightly_exp * total_room_nights, 'USD', target_currency)
        h_max = CurrencyConverter.convert(nightly_max * total_room_nights, 'USD', target_currency)
        hotel_rate = CurrencyConverter.get_rate('USD', target_currency)

        budget_lines_to_create.append(ScenarioBudgetLine(
            hospital_scenario=scenario,
            expense_category=ScenarioBudgetLine.ExpenseCategory.ACCOMMODATION,
            description=f"Medical & Recovery Lodging ({stay_nights} nights × {rooms_needed} room{'s' if rooms_needed > 1 else ''})",
            min_amount=nightly_min * total_room_nights,
            expected_amount=nightly_exp * total_room_nights,
            max_amount=nightly_max * total_room_nights,
            source_currency='USD',
            scenario_currency=target_currency,
            exchange_rate_snapshot=hotel_rate,
            converted_expected_amount=h_exp,
            quantity=decimal.Decimal(str(total_room_nights)),
            unit='room_nights',
            data_classification=DataClassification.INDICATIVE
        ))

        # 4. Medical Visa & Government Processing (VC_s)
        # $80 per traveler
        visa_unit = decimal.Decimal('80.00')
        v_exp = CurrencyConverter.convert(visa_unit * party_size, 'USD', target_currency)
        v_rate = CurrencyConverter.get_rate('USD', target_currency)

        budget_lines_to_create.append(ScenarioBudgetLine(
            hospital_scenario=scenario,
            expense_category=ScenarioBudgetLine.ExpenseCategory.VISA,
            description=f"Medical Visa Application Fees ({party_size} traveler{'s' if party_size > 1 else ''})",
            min_amount=visa_unit * party_size,
            expected_amount=visa_unit * party_size,
            max_amount=(visa_unit + decimal.Decimal('20.00')) * party_size,
            source_currency='USD',
            scenario_currency=target_currency,
            exchange_rate_snapshot=v_rate,
            converted_expected_amount=v_exp,
            quantity=decimal.Decimal(str(party_size)),
            unit='visas',
            data_classification=DataClassification.INDICATIVE
        ))

        # 5. Local Hospital & Airport Transfers (LC_s)
        l_exp = CurrencyConverter.convert(decimal.Decimal('150.00'), 'USD', target_currency)
        l_rate = CurrencyConverter.get_rate('USD', target_currency)

        budget_lines_to_create.append(ScenarioBudgetLine(
            hospital_scenario=scenario,
            expense_category=ScenarioBudgetLine.ExpenseCategory.LOCAL_TRANSPORT,
            description="Dedicated Airport, Clinical & Hotel Private Transfers",
            min_amount=decimal.Decimal('100.00'),
            expected_amount=decimal.Decimal('150.00'),
            max_amount=decimal.Decimal('220.00'),
            source_currency='USD',
            scenario_currency=target_currency,
            exchange_rate_snapshot=l_rate,
            converted_expected_amount=l_exp,
            quantity=decimal.Decimal('1.00'),
            unit='transit package',
            data_classification=DataClassification.INDICATIVE
        ))

        # 6. Miscellaneous & Medical Contingency Reserve (MC_s)
        m_exp = CurrencyConverter.convert(decimal.Decimal('200.00'), 'USD', target_currency)
        m_rate = CurrencyConverter.get_rate('USD', target_currency)

        budget_lines_to_create.append(ScenarioBudgetLine(
            hospital_scenario=scenario,
            expense_category=ScenarioBudgetLine.ExpenseCategory.MISCELLANEOUS,
            description="Contingency Reserve, Incidentals & Pharmacy Supplies",
            min_amount=decimal.Decimal('150.00'),
            expected_amount=decimal.Decimal('200.00'),
            max_amount=decimal.Decimal('350.00'),
            source_currency='USD',
            scenario_currency=target_currency,
            exchange_rate_snapshot=m_rate,
            converted_expected_amount=m_exp,
            quantity=decimal.Decimal('1.00'),
            unit='contingency',
            data_classification=DataClassification.INDICATIVE
        ))

        # Bulk save
        created_lines = ScenarioBudgetLine.objects.bulk_create(budget_lines_to_create)

        # Financial Ledger Summation
        total_budget = trip_request.total_budget_amount or decimal.Decimal('0.00')
        converted_total_budget = CurrencyConverter.convert(
            total_budget,
            trip_request.budget_currency or 'USD',
            target_currency
        )

        mandatory_expenditure = sum(line.converted_expected_amount for line in created_lines)
        discretionary_budget = converted_total_budget - mandatory_expenditure
        reserve_amount = (converted_total_budget * self.reserve_percentage).quantize(decimal.Decimal('0.01'))
        spendable_tourism_budget = max(decimal.Decimal('0.00'), discretionary_budget - reserve_amount)

        is_over_budget = discretionary_budget < 0
        shortfall = abs(discretionary_budget) if is_over_budget else decimal.Decimal('0.00')

        return {
            'scenario_id': str(scenario.id),
            'currency': target_currency,
            'total_budget': converted_total_budget,
            'mandatory_expenditure': mandatory_expenditure,
            'discretionary_budget': discretionary_budget,
            'contingency_reserve': reserve_amount,
            'spendable_tourism_budget': spendable_tourism_budget,
            'is_over_budget': is_over_budget,
            'shortfall': shortfall,
            'line_count': len(created_lines)
        }

