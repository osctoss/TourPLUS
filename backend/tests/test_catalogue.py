from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class CatalogueApiTest(TestCase):
    fixtures = []

    def setUp(self):
        from django.core.management import call_command
        call_command('seed_catalogue')

    def test_specialties_catalogue_endpoint(self):
        url = reverse('medical:specialty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 3)
        specialty_slugs = [s['slug'] for s in results]
        self.assertIn('cardiology', specialty_slugs)
        self.assertIn('orthopedics', specialty_slugs)
        self.assertIn('oncology', specialty_slugs)

    def test_hospitals_catalogue_and_filtering(self):
        url = reverse('hospitals:hospital-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertGreaterEqual(len(results), 20)

        # Test search by hospital name
        search_res = self.client.get(f"{url}?search=Medanta")
        self.assertEqual(search_res.status_code, status.HTTP_200_OK)
        search_data = search_res.json()
        search_results = search_data.get('results', search_data)
        self.assertGreaterEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['name'], 'Medanta The Medicity')

    def test_destinations_catalogue(self):
        url = reverse('tourism:tourist-destination-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get('count'), 50)
        results = data.get('results', data)
        self.assertEqual(len(results), 20)

    def test_travel_packages_and_inclusions(self):
        url = reverse('packages:package-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertGreaterEqual(len(results), 5)

        # Inspect first package has inclusions
        pkg = results[0]
        self.assertTrue(len(pkg['inclusions']) > 0)
        self.assertTrue(len(pkg['package_destinations']) > 0)
