from django.test import TestCase
from rest_framework.exceptions import ValidationError
from tutoring.models import TutoringYear, TutoringTerm, TutoringWeek
from api.utils import parse_term, validate_term_format, fetch_term, collateAnalyticsAmountOfEnrolments

class UtilsTest(TestCase):

    def setUp(self):
        # Setup years and terms for tests
        self.year = TutoringYear.objects.create(index=24)
        for term_index in range(1, 5):
            TutoringTerm.objects.create(index=term_index, year=self.year)

        # Fetch term objects for analytics tests
        self.term1 = fetch_term({"year": 24, "term": 1})
        self.term2 = fetch_term({"year": 24, "term": 2})
        self.term3 = fetch_term({"year": 24, "term": 3})

        # Link previousTerm
        self.term2.previousTerm = self.term1
        self.term3.previousTerm = self.term2

        # Add weeks for each term
        for term in [self.term1, self.term2, self.term3]:
            for i in range(1, 4):
                TutoringWeek.objects.create(index=i, term=term)

        # Patch amountOfEnrolments for deterministic tests
        self.term1.amountOfEnrolments = lambda: 100
        self.term2.amountOfEnrolments = lambda: 120
        self.term3.amountOfEnrolments = lambda: 80

    # ---------------------
    # parse_term tests
    # ---------------------
    def test_parse_term_valid(self):
        term_str = "24T3"
        parsed = parse_term(term_str)
        self.assertEqual(parsed, {"year": 24, "term": 3})

        term_str = "24t1"  # lowercase
        parsed = parse_term(term_str)
        self.assertEqual(parsed, {"year": 24, "term": 1})

    def test_parse_term_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            parse_term("2024-01-01")
        self.assertIn("Invalid term format", str(cm.exception))

        with self.assertRaises(ValidationError) as cm:
            parse_term("24T12")
        self.assertIn("Invalid term format", str(cm.exception))

        with self.assertRaises(ValidationError) as cm:
            parse_term("24X3")
        self.assertIn("Invalid term format", str(cm.exception))

    # ---------------------
    # validate_term_format tests
    # ---------------------
    def test_validate_term_format_valid(self):
        try:
            validate_term_format("24T3")
        except ValidationError:
            self.fail("validate_term_format raised ValidationError unexpectedly!")

    def test_validate_term_format_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            validate_term_format("invalid")
        self.assertIn("Invalid term format", str(cm.exception))

    # ---------------------
    # fetch_term tests
    # ---------------------
    def test_fetch_term_exists(self):
        term_dict = {"year": 24, "term": 3}
        term_obj = fetch_term(term_dict)
        self.assertEqual(term_obj.index, 3)
        self.assertEqual(term_obj.year.index, 24)

    def test_fetch_term_nonexistent_year(self):
        term_dict = {"year": 99, "term": 1}
        with self.assertRaises(ValidationError) as cm:
            fetch_term(term_dict)
        self.assertEqual(cm.exception.detail["Ranges"], "One or more of the ranges don't exist")

    def test_fetch_term_nonexistent_term(self):
        term_dict = {"year": 24, "term": 99}
        with self.assertRaises(ValidationError) as cm:
            fetch_term(term_dict)
        self.assertEqual(cm.exception.detail["Ranges"], "One or more of the ranges don't exist")

    # ---------------------
    # collateAnalyticsAmountOfEnrolments tests
    # ---------------------
    def test_collate_analytics_increase(self):
        result = collateAnalyticsAmountOfEnrolments(self.term2)
        self.assertEqual(result["amountOfEnrolments"], 120)
        self.assertEqual(result["trend"], "+")
        self.assertAlmostEqual(result["percentageChangeFromPrevTerm"], 20.0)

    def test_collate_analytics_decrease(self):
        result = collateAnalyticsAmountOfEnrolments(self.term3)
        self.assertEqual(result["amountOfEnrolments"], 80)
        self.assertEqual(result["trend"], "-")
        self.assertAlmostEqual(result["percentageChangeFromPrevTerm"], -33.333333, places=3)

    def test_collate_analytics_no_previous_term(self):
        result = collateAnalyticsAmountOfEnrolments(self.term1)
        self.assertEqual(result["amountOfEnrolments"], 100)
        self.assertIsNone(result["trend"])
        self.assertIsNone(result["percentageChangeFromPrevTerm"])

    def test_collate_analytics_previous_term_zero(self):
        self.term1.amountOfEnrolments = lambda: 0
        result = collateAnalyticsAmountOfEnrolments(self.term2)
        self.assertEqual(result["amountOfEnrolments"], 120)
        self.assertEqual(result["trend"], "+")
        self.assertEqual(result["percentageChangeFromPrevTerm"], 100.0)

    def test_collate_analytics_no_change(self):
        self.term2.amountOfEnrolments = lambda: 100
        result = collateAnalyticsAmountOfEnrolments(self.term2)
        self.assertEqual(result["amountOfEnrolments"], 100)
        self.assertEqual(result["trend"], "+")
        self.assertEqual(result["percentageChangeFromPrevTerm"], 0.0)
