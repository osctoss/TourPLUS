from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import User, PatientProfile, ConsentRecord


class AuthApiTest(TestCase):
    def test_patient_registration_and_profile_creation(self):
        url = reverse('accounts:register')
        payload = {
            'email': 'patient.test@example.com',
            'password': 'SecurePassword123!',
            'full_name': 'Sarah Jenkins',
            'origin_country_code': 'GB',
            'display_currency': 'GBP',
            'consent_accepted': True
        }
        response = self.client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify User created with UUID and proper role
        user = User.objects.get(email='patient.test@example.com')
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertTrue(user.is_active)
        
        # Verify PatientProfile created
        profile = PatientProfile.objects.get(user=user)
        self.assertEqual(profile.full_name, 'Sarah Jenkins')
        self.assertEqual(profile.origin_country_code, 'GB')
        self.assertEqual(profile.display_currency, 'GBP')

        # Verify ConsentRecord created
        consent = ConsentRecord.objects.get(user=user)
        self.assertEqual(consent.consent_type, 'PRIVACY_AND_DATA_PROCESSING')

    def test_login_and_current_user_flow(self):
        user = User.objects.create_user(email='jane.doe@example.com', password='Password123!', role=User.Role.PATIENT)
        PatientProfile.objects.create(user=user, full_name='Jane Doe')

        login_url = reverse('accounts:login')
        login_res = self.client.post(login_url, {'email': 'jane.doe@example.com', 'password': 'Password123!'}, content_type='application/json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

        me_url = reverse('accounts:me')
        me_res = self.client.get(me_url)
        self.assertEqual(me_res.status_code, status.HTTP_200_OK)
        self.assertEqual(me_res.json()['user']['email'], 'jane.doe@example.com')
        self.assertEqual(me_res.json()['profile']['full_name'], 'Jane Doe')

