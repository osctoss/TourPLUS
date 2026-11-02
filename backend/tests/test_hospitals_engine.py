import decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from apps.medical.models import Specialty, TreatmentCategory
from apps.trip_planning.models import TripRequest
from engines.hospitals.ranking import HospitalRankingEngine

User = get_user_model()


class HospitalRankingEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalogue')
        cls.user = User.objects.create_user(
            email='testpatient@example.com',
            password='SecurePassword123!'
        )
        cls.cardiology = Specialty.objects.get(slug='cardiology')
        cls.cabg = TreatmentCategory.objects.get(slug='cabg')

    def test_ranking_evaluates_cardiology_hospitals(self):
        engine = HospitalRankingEngine()
        eligible, excluded = engine.evaluate_candidates(
            specialty_id=str(self.cardiology.id),
            treatment_category_id=str(self.cabg.id),
            total_budget=decimal.Decimal('15000.00')
        )
        self.assertGreater(len(eligible), 0)
        # Verify rank ordering
        scores = [item['score'] for item in eligible]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for item in eligible:
            self.assertIn('treatment_match', item['breakdown'])
            self.assertIn('cost_suitability', item['breakdown'])

    def test_trip_request_generate_plan_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        trip_req = TripRequest.objects.create(
            user=self.user,
            specialty=self.cardiology,
            treatment_category=self.cabg,
            total_budget_amount=decimal.Decimal('20000.00'),
            budget_currency='USD',
            party_size=2,
            available_days=14,
            recovery_duration_days=7,
            clinician_travel_guidance_status=TripRequest.ClinicianGuidance.PROVIDED
        )

        response = client.post(f'/api/v1/trip-requests/{trip_req.id}/generate-plan/')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'COMPLETED')
        self.assertGreater(len(data['scenarios']), 0)

        # Reload trip request
        trip_req.refresh_from_db()
        self.assertEqual(trip_req.status, TripRequest.Status.COMPLETED)
