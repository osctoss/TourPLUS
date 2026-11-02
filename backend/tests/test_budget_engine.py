import decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from apps.medical.models import Specialty, TreatmentCategory
from apps.hospitals.models import HospitalTreatmentOffering
from apps.trip_planning.models import TripRequest
from apps.recommendations.models import RecommendationRun, HospitalScenario, ScenarioBudgetLine
from engines.budgeting.ledger import BudgetLedgerEngine

User = get_user_model()


class BudgetLedgerEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalogue')
        cls.user = User.objects.create_user(
            email='budgetpatient@example.com',
            password='Password123!'
        )
        cls.specialty = Specialty.objects.get(slug='orthopedics')
        cls.category = TreatmentCategory.objects.get(slug='total-knee-replacement')
        cls.offering = HospitalTreatmentOffering.objects.filter(treatment_category=cls.category).first()

    def test_decimal_precision_and_ledger_summation(self):
        trip_req = TripRequest.objects.create(
            user=self.user,
            specialty=self.specialty,
            treatment_category=self.category,
            total_budget_amount=decimal.Decimal('18500.00'),
            budget_currency='USD',
            party_size=2,
            available_days=14,
            recovery_duration_days=10
        )
        run = RecommendationRun.objects.create(trip_request=trip_req)
        scenario = HospitalScenario.objects.create(
            recommendation_run=run,
            hospital_treatment_offering=self.offering,
            scenario_currency='USD'
        )

        engine = BudgetLedgerEngine()
        summary = engine.build_scenario_budget(scenario, trip_req)

        self.assertFalse(summary['is_over_budget'])
        self.assertEqual(summary['shortfall'], decimal.Decimal('0.00'))
        self.assertGreater(summary['mandatory_expenditure'], decimal.Decimal('0.00'))
        self.assertGreater(summary['discretionary_budget'], decimal.Decimal('0.00'))

        # Verify line-by-line summation matches mandatory_expenditure exactly
        lines = scenario.budget_lines.all()
        computed_sum = sum(line.converted_expected_amount for line in lines)
        self.assertEqual(summary['mandatory_expenditure'], computed_sum)

        # Verify categories present
        cats = set(lines.values_list('expense_category', flat=True))
        self.assertIn(ScenarioBudgetLine.ExpenseCategory.TREATMENT, cats)
        self.assertIn(ScenarioBudgetLine.ExpenseCategory.ACCOMMODATION, cats)
        self.assertIn(ScenarioBudgetLine.ExpenseCategory.INTERNATIONAL_FLIGHT, cats)
        self.assertIn(ScenarioBudgetLine.ExpenseCategory.VISA, cats)

    def test_over_budget_detection_and_shortfall(self):
        # Patient with insufficient budget ($2,000 for knee replacement + flights)
        trip_req = TripRequest.objects.create(
            user=self.user,
            specialty=self.specialty,
            treatment_category=self.category,
            total_budget_amount=decimal.Decimal('2000.00'),
            budget_currency='USD',
            party_size=1,
            available_days=7
        )
        run = RecommendationRun.objects.create(trip_request=trip_req)
        scenario = HospitalScenario.objects.create(
            recommendation_run=run,
            hospital_treatment_offering=self.offering,
            scenario_currency='USD'
        )

        engine = BudgetLedgerEngine()
        summary = engine.build_scenario_budget(scenario, trip_req)

        self.assertTrue(summary['is_over_budget'])
        self.assertGreater(summary['shortfall'], decimal.Decimal('0.00'))
        self.assertEqual(summary['spendable_tourism_budget'], decimal.Decimal('0.00'))
