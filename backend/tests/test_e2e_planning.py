from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from apps.medical.models import Specialty, TreatmentCategory
from apps.tourism.models import DestinationCategory, TouristDestination
from apps.trip_planning.models import TripRequest

User = get_user_model()


class EndToEndPlanningJourneyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalogue')
        cls.user = User.objects.create_user(
            email='e2epatient@example.com',
            password='ComplexPassword123!'
        )
        cls.specialty = Specialty.objects.get(slug='cardiology')
        cls.category = TreatmentCategory.objects.get(slug='cabg')
        cls.heritage = DestinationCategory.objects.get(slug='heritage-history')

    def test_complete_user_planning_journey(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        # Step 1: Create Trip Request with interest preferences
        create_resp = client.post('/api/v1/trip-requests/', {
            'specialty': str(self.specialty.id),
            'treatment_category': str(self.category.id),
            'known_condition_text': 'Patient diagnosed with 3-vessel coronary artery disease. Needs bypass graft.',
            'total_budget_amount': '22000.00',
            'budget_currency': 'USD',
            'party_size': 2,
            'available_days': 15,
            'recovery_duration_days': 7,
            'clinician_travel_guidance_status': TripRequest.ClinicianGuidance.PROVIDED,
            'travel_intensity_preference': TripRequest.TravelIntensity.LOW,
            'interests_input': [
                {'destination_category': str(self.heritage.id), 'preference_weight': 5}
            ]
        }, format='json')
        self.assertEqual(create_resp.status_code, 201)
        trip_req_id = create_resp.json()['id']

        # Step 2: Trigger Plan Generation
        gen_resp = client.post(f'/api/v1/trip-requests/{trip_req_id}/generate-plan/')
        self.assertEqual(gen_resp.status_code, 201)
        rec_data = gen_resp.json()
        self.assertEqual(rec_data['status'], 'COMPLETED')
        self.assertGreater(len(rec_data['scenarios']), 0)

        chosen_scenario = rec_data['scenarios'][0]
        scenario_id = chosen_scenario['id']

        # Step 3: Inspect Scenario Destinations & Packages
        dest_resp = client.get(f'/api/v1/recommendations/scenarios/{scenario_id}/destinations/')
        self.assertEqual(dest_resp.status_code, 200)
        destinations = dest_resp.json()
        self.assertGreater(len(destinations), 0)

        pkg_resp = client.get(f'/api/v1/recommendations/scenarios/{scenario_id}/packages/')
        self.assertEqual(pkg_resp.status_code, 200)
        packages = pkg_resp.json()
        self.assertGreater(len(packages), 0)

        chosen_package_id = packages[0]['id']
        sample_dest = TouristDestination.objects.first()

        # Step 4: Save Final Plan
        final_resp = client.post('/api/v1/final-plans/', {
            'hospital_scenario': scenario_id,
            'package_match': chosen_package_id,
            'plan_title': 'My India Cardiac Care & Recovery Trip',
            'selected_scope': 'LOCAL_REGIONAL',
            'destinations_input': [
                {
                    'destination': str(sample_dest.id),
                    'sequence_order': 1,
                    'planned_duration_minutes': 120,
                    'notes': 'Gentle afternoon walking tour post-discharge'
                }
            ]
        }, format='json')
        self.assertEqual(final_resp.status_code, 201)
        plan_id = final_resp.json()['id']

        # Step 5: Export Plan Summary
        export_resp = client.get(f'/api/v1/final-plans/{plan_id}/export/')
        self.assertEqual(export_resp.status_code, 200)
        export_data = export_resp.json()

        self.assertIn('financial_ledger', export_data)
        self.assertIn('hospital', export_data)
        self.assertIn('tourism_itinerary', export_data)
        self.assertIn('disclaimers', export_data)
        self.assertIn('medical_safety', export_data['disclaimers'])
        self.assertIn('package_inclusion_credit', export_data['financial_ledger'])

