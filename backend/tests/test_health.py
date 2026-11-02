from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class HealthCheckApiTest(TestCase):
    def test_health_check_endpoint(self):
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('product'), 'TourPlus AI')
        self.assertEqual(data.get('version'), '1.0.0')
        self.assertEqual(data.get('database'), 'ok')

