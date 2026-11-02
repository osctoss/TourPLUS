import decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from apps.medical.models import Specialty, TreatmentCategory
from apps.hospitals.models import HospitalTreatmentOffering
from apps.trip_planning.models import TripRequest
from apps.recommendations.models import RecommendationRun, HospitalScenario
from engines.budgeting.ledger import BudgetLedgerEngine
from engines.tourism.recommender import TourismRecommendationEngine
from engines.package_matching.matcher import PackageMatchingEngine

User = get_user_model()


class PackageMatchingEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalogue')
        cls.user = User.objects.create_user(
            email='packagepatient@example.com',
            password='Password123!'
        )
        cls.specialty = Specialty.objects.get(slug='oncology')
        cls.category = TreatmentCategory.objects.get(slug='medical-oncology')
        cls.offering = HospitalTreatmentOffering.objects.filter(treatment_category=cls.category).first()

    def test_dynamic_inclusion_credit_and_effective_cost(self):
        trip_req = TripRequest.objects.create(
            user=self.user,
            specialty=self.specialty,
            treatment_category=self.category,
            total_budget_amount=decimal.Decimal('25000.00'),
            budget_currency='USD',
            party_size=1,
            available_days=14
        )
        run = RecommendationRun.objects.create(trip_request=trip_req)
        scenario = HospitalScenario.objects.create(
            recommendation_run=run,
            hospital_treatment_offering=self.offering,
            scenario_currency='USD'
        )

        # 1. Budget lines
        budget_summary = BudgetLedgerEngine().build_scenario_budget(scenario, trip_req)
        # 2. Tourism
        TourismRecommendationEngine().recommend_destinations(scenario, trip_req, budget_summary['discretionary_budget'])
        # 3. Package Matching
        matches = PackageMatchingEngine().match_packages(scenario, budget_summary['discretionary_budget'], trip_req.party_size)

        self.assertGreater(len(matches), 0)

        for match in matches:
            # Mathematical consistency: Effective Cost = Listed Price - Inclusion Credit
            self.assertEqual(
                match.effective_incremental_cost,
                max(decimal.Decimal('0.00'), match.listed_package_price - match.inclusion_credit)
            )
            # Remaining budget = Discretionary Budget - Effective Cost
            self.assertEqual(
                match.remaining_discretionary_budget,
                budget_summary['discretionary_budget'] - match.effective_incremental_cost
            )
            # Credits must have reasons and point to valid budget lines
            for cr in match.credits.all():
                self.assertGreater(cr.credited_amount, decimal.Decimal('0.00'))
                self.assertTrue(len(cr.credit_reason) > 0)
                self.assertEqual(cr.scenario_budget_line.hospital_scenario, scenario)

