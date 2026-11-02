import decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from apps.medical.models import Specialty, TreatmentCategory
from apps.hospitals.models import HospitalTreatmentOffering
from apps.trip_planning.models import TripRequest
from apps.recommendations.models import RecommendationRun, HospitalScenario, DestinationRecommendation
from engines.tourism.recommender import TourismRecommendationEngine

User = get_user_model()


class TourismEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalogue')
        cls.user = User.objects.create_user(
            email='touristpatient@example.com',
            password='Password123!'
        )
        cls.specialty = Specialty.objects.get(slug='cardiology')
        cls.category = TreatmentCategory.objects.get(slug='cabg')
        cls.offering = HospitalTreatmentOffering.objects.filter(treatment_category=cls.category).first()

    def test_three_tier_classification_and_clinical_review_boundary(self):
        # Patient with no confirmed clinician guidance
        trip_req = TripRequest.objects.create(
            user=self.user,
            specialty=self.specialty,
            treatment_category=self.category,
            total_budget_amount=decimal.Decimal('15000.00'),
            clinician_travel_guidance_status=TripRequest.ClinicianGuidance.NOT_PROVIDED,
            travel_intensity_preference=TripRequest.TravelIntensity.LOW
        )
        run = RecommendationRun.objects.create(trip_request=trip_req)
        scenario = HospitalScenario.objects.create(
            recommendation_run=run,
            hospital_treatment_offering=self.offering,
            scenario_currency='USD'
        )

        engine = TourismRecommendationEngine()
        created = engine.recommend_destinations(
            scenario=scenario,
            trip_request=trip_req,
            discretionary_budget=decimal.Decimal('3500.00')
        )

        self.assertGreater(len(created), 0)

        # Verify all 3 scopes exist
        scopes = set(r.tourism_scope for r in created)
        self.assertIn(DestinationRecommendation.Scope.LOCAL_REGIONAL, scopes)
        self.assertIn(DestinationRecommendation.Scope.STATE_LEVEL, scopes)
        self.assertIn(DestinationRecommendation.Scope.NATIONAL, scopes)

        # Crucial clinical boundary: unguided patient must receive REQUIRES_CLINICAL_REVIEW
        for rec in created:
            self.assertEqual(rec.feasibility_status, DestinationRecommendation.Feasibility.REQUIRES_CLINICAL_REVIEW)
            self.assertEqual(rec.recovery_review_status, 'REQUIRES_CLINICIAN_CONFIRMATION')

    def test_clinically_permitted_guidance(self):
        # Patient with confirmed clinician guidance
        trip_req = TripRequest.objects.create(
            user=self.user,
            specialty=self.specialty,
            treatment_category=self.category,
            total_budget_amount=decimal.Decimal('15000.00'),
            clinician_travel_guidance_status=TripRequest.ClinicianGuidance.PROVIDED,
            travel_intensity_preference=TripRequest.TravelIntensity.MODERATE
        )
        run = RecommendationRun.objects.create(trip_request=trip_req)
        scenario = HospitalScenario.objects.create(
            recommendation_run=run,
            hospital_treatment_offering=self.offering,
            scenario_currency='USD'
        )

        engine = TourismRecommendationEngine()
        created = engine.recommend_destinations(
            scenario=scenario,
            trip_request=trip_req,
            discretionary_budget=decimal.Decimal('3500.00')
        )

        # Low/moderate intensity destinations should be FEASIBLE
        feasible_recs = [r for r in created if r.feasibility_status == DestinationRecommendation.Feasibility.FEASIBLE]
        self.assertGreater(len(feasible_recs), 0)

