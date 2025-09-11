import datetime
import json
from pathlib import Path
from rest_framework.test import APITestCase
from stripeInt.models import StripeProd
from tutoring.models import Group

class GroupApiTest(APITestCase):

  def setUp(self):
    prod = StripeProd.objects.create(
        stripeId="prod_test123",
        defaultPriceId="price_test123",
        name="Tutoring Product",
        is_active=True
    )

    # 2. Create some groups
    group1 = Group.objects.create(
        lesson_length=1,
        associated_product=prod,
        tutor="Alice",
        course=Group.CourseChoices.JUNIOR_MATHS,
        day_of_week=Group.Weekday.MONDAY,
        time_of_day=datetime.time(16, 0)  # 4:00 PM
    )

    group2 = Group.objects.create(
        lesson_length=2,
        associated_product=prod,
        tutor="Bob",
        course=Group.CourseChoices.YEAR11_ADV,
        day_of_week=Group.Weekday.WEDNESDAY,
        time_of_day=datetime.time(18, 30)  # 6:30 PM
    )

    group3 = Group.objects.create(
        lesson_length=1,
        associated_product=prod,
        tutor="Charlie",
        course=Group.CourseChoices.YEAR12_EXT1,
        day_of_week=Group.Weekday.SATURDAY,
        time_of_day=datetime.time(10, 0)  # 10:00 AM
    )

  def test_list_all_groups(self):
    actual = self.client.get('/api/groups/').data
    expected = json.loads((Path(__file__).parent / "fixtures/GroupApiTest/test_list_all_groups.json").read_text())
    self.assertEqual(actual, expected)