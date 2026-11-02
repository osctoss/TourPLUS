import decimal
from typing import List, Dict, Any
from apps.recommendations.models import (
    HospitalScenario,
    PackageMatch,
    PackageMatchInclusionCredit
)
from apps.packages.models import TravelPackage, PackageInclusion
from integrations.exchange_rates.converter import CurrencyConverter


class PackageMatchingEngine:
    """
    Dynamic Travel Package Matching & Inclusion Credit Engine.
    Matches published packages with recommended scenario destinations and calculates:
      1. Destination coverage
      2. Dynamic inclusion credit: Credit_{p,c} = min(B_c, V_{p,c})
      3. Effective incremental cost: EPC_p = P_p - I_p
      4. Remaining discretionary budget: R_p = DB_{0,s} - EPC_p
    Guarantees no double-counting of mandatory stay expenses.
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            'coverage': 0.45,
            'cost_efficiency': 0.20,
            'itinerary_fit': 0.20,
            'service_completeness': 0.10,
            'agency_confidence': 0.05
        }

    def match_packages(
        self,
        scenario: HospitalScenario,
        discretionary_budget: decimal.Decimal,
        party_size: int = 1
    ) -> List[PackageMatch]:
        """
        Calculates package matches, derives Dynamic Inclusion Credits, and persists results.
        """
        # Clear existing matches for idempotency
        scenario.package_matches.all().delete()

        recommended_dest_ids = set(
            scenario.destinations.values_list('destination_id', flat=True)
        )
        total_rec_count = len(recommended_dest_ids)

        # Map budget lines by category for quick lookup
        budget_lines_by_category = {
            line.expense_category: line
            for line in scenario.budget_lines.all()
        }

        published_packages = TravelPackage.objects.filter(
            is_published=True
        ).select_related('agency').prefetch_related(
            'package_destinations__destination',
            'inclusions'
        )

        matched_packages_data: List[Dict[str, Any]] = []
        target_currency = scenario.scenario_currency or 'USD'

        for package in published_packages:
            pkg_dest_ids = set(
                package.package_destinations.values_list('destination_id', flat=True)
            )

            # 1. Coverage Calculation
            if total_rec_count > 0:
                overlap = recommended_dest_ids.intersection(pkg_dest_ids)
                coverage_score = len(overlap) / float(total_rec_count)
            else:
                coverage_score = 0.50

            # 2. Package Price Normalization
            # If price basis is per person, multiply by party size
            raw_pkg_price = package.price_amount or decimal.Decimal('0.00')
            if package.price_basis == TravelPackage.PriceBasis.PER_PERSON:
                total_pkg_price = raw_pkg_price * decimal.Decimal(str(party_size))
            else:
                total_pkg_price = raw_pkg_price

            converted_pkg_price = CurrencyConverter.convert(
                total_pkg_price,
                package.currency,
                target_currency
            )

            # 3. Dynamic Inclusion Credit Ledger (Credit_{p,c} = min(B_c, V_{p,c}))
            inclusion_credits: List[Dict[str, Any]] = []
            total_credit = decimal.Decimal('0.00')

            for inc in package.inclusions.filter(inclusion_status=PackageInclusion.Status.INCLUDED):
                equiv_cat = inc.equivalent_budget_category
                if not equiv_cat or equiv_cat in [
                    PackageInclusion.EquivalentCategory.MISCELLANEOUS,
                    PackageInclusion.EquivalentCategory.NONE
                ]:
                    # Sightseeing, tour guides, and meals do not receive mandatory credit
                    continue

                matching_budget_line = budget_lines_by_category.get(equiv_cat)
                if not matching_budget_line:
                    continue

                b_c = matching_budget_line.converted_expected_amount
                # Service value of inclusion
                if inc.service_value_amount and inc.service_value_amount > 0:
                    val_converted = CurrencyConverter.convert(
                        inc.service_value_amount * (party_size if inc.unit in ['person', 'ticket'] else 1),
                        inc.service_value_currency or package.currency,
                        target_currency
                    )
                else:
                    # If service value not explicitly recorded, estimate conservative value
                    val_converted = b_c * decimal.Decimal('0.50')

                # Strict double-counting prevention: Credit = min(B_c, V_{p,c})
                credit_amount = min(b_c, val_converted)

                if credit_amount > 0:
                    total_credit += credit_amount
                    inclusion_credits.append({
                        'inclusion': inc,
                        'budget_line': matching_budget_line,
                        'amount': credit_amount,
                        'reason': (
                            f"Inclusion '{inc.description}' offsets mandatory "
                            f"{matching_budget_line.get_expense_category_display()} budgeted expense."
                        )
                    })

            # 4. Effective Incremental Package Cost (EPC_p = P_p - I_p)
            effective_cost = max(decimal.Decimal('0.00'), converted_pkg_price - total_credit)

            # 5. Remaining Discretionary Budget (R_p = DB_{0,s} - EPC_p)
            remaining_budget = discretionary_budget - effective_cost
            feasibility = (
                PackageMatch.Feasibility.FEASIBLE
                if remaining_budget >= 0
                else PackageMatch.Feasibility.OVER_BUDGET
            )

            # 6. Multi-Criteria Package Ranking Score (PScore)
            # Cost efficiency: reward packages whose effective cost fits comfortably
            if discretionary_budget > 0:
                cost_eff_score = max(0.1, min(1.0, float(decimal.Decimal('1.0') - (effective_cost / discretionary_budget) * decimal.Decimal('0.6'))))
            else:
                cost_eff_score = 0.2

            itinerary_fit = min(1.0, 0.70 + (0.10 * min(3, len(pkg_dest_ids))))
            service_comp = 0.85 if len(inclusion_credits) >= 2 else 0.65
            agency_conf = 0.90 if package.agency.verification_status == 'VERIFIED' else 0.70

            w = self.weights
            p_score = (
                w['coverage'] * coverage_score +
                w['cost_efficiency'] * cost_eff_score +
                w['itinerary_fit'] * itinerary_fit +
                w['service_completeness'] * service_comp +
                w['agency_confidence'] * agency_conf
            )

            matched_packages_data.append({
                'package': package,
                'coverage_score': decimal.Decimal(str(round(coverage_score, 4))),
                'inclusion_credit': total_credit,
                'listed_price': converted_pkg_price,
                'effective_cost': effective_cost,
                'remaining_budget': remaining_budget,
                'feasibility': feasibility,
                'itinerary_fit_score': decimal.Decimal(str(round(itinerary_fit, 4))),
                'agency_reliability_score': decimal.Decimal(str(round(agency_conf, 4))),
                'overall_score': decimal.Decimal(str(round(p_score, 4))),
                'explanation': (
                    f"Features {len(pkg_dest_ids)} curated destinations. Dynamic Inclusion Credit: "
                    f"{target_currency} {total_credit:.2f} deducted to prevent duplicate lodging/flight costs."
                ),
                'credits_data': inclusion_credits
            })

        # Rank packages descending by overall score
        matched_packages_data.sort(key=lambda x: x['overall_score'], reverse=True)

        created_matches: List[PackageMatch] = []
        for rank_idx, data in enumerate(matched_packages_data, start=1):
            match_obj = PackageMatch.objects.create(
                hospital_scenario=scenario,
                travel_package=data['package'],
                rank=rank_idx,
                destination_coverage_score=data['coverage_score'],
                inclusion_credit=data['inclusion_credit'],
                listed_package_price=data['listed_price'],
                effective_incremental_cost=data['effective_cost'],
                remaining_discretionary_budget=data['remaining_budget'],
                budget_feasibility_status=data['feasibility'],
                itinerary_fit_score=data['itinerary_fit_score'],
                agency_reliability_score=data['agency_reliability_score'],
                overall_score=data['overall_score'],
                explanation=data['explanation']
            )

            # Persist dynamic inclusion credit line items
            for cr in data['credits_data']:
                PackageMatchInclusionCredit.objects.create(
                    package_match=match_obj,
                    package_inclusion=cr['inclusion'],
                    scenario_budget_line=cr['budget_line'],
                    credited_amount=cr['amount'],
                    credited_currency=target_currency,
                    credit_reason=cr['reason']
                )

            created_matches.append(match_obj)

        return created_matches
