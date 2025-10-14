from rest_framework.test import APITestCase
from tutoring.models import TutoringTerm, TutoringWeek, TutoringYear

class AnalyticsEndpointTest(APITestCase):
    def setUp(self):
        self.url = '/api/analytics/'
        # Create a year
        self.year = TutoringYear.objects.create(index=23)

        # Create 4 terms with 10 weeks each
        for term_index in range(1, 5):
            term = TutoringTerm.objects.create(index=term_index, year=self.year)
            for week_index in range(1, 11):  # assuming 10 weeks per term
                TutoringWeek.objects.create(index=week_index, term=term)

    def testInvalidTermFormat(self):
        response = self.client.get(self.url, {'term': '2024-01-01'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['term'],
            "Invalid term format. Expected format like '24T3'."
        )

    def testTermDoesNotExist(self):
        response = self.client.get(self.url, {'term': '99T3'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['Ranges'],
            "One or more of the ranges don't exist"
        )

    def testValidTerm(self):
        response = self.client.get(self.url, {'term': '23T1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('amount_of_enrolments', response.data)
