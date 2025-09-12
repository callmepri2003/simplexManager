import datetime
import json
from pathlib import Path
from rest_framework.test import APITestCase
from stripeInt.models import StripeProd
from tutoring.models import Group, Lesson, Parent, TutoringStudent
from rest_framework import status
from django.urls import reverse

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

class BulkAddAttendancesTests(APITestCase):
    def setUp(self):
        # 1. Create Stripe Product (required for Group.associated_product)
        self.prod = StripeProd.objects.create(
            stripeId="prod_test123",
            defaultPriceId="price_test123",
            name="Tutoring Product",
            is_active=True
        )

        # 2. Create a Group
        self.group = Group.objects.create(
            lesson_length=1,
            associated_product=self.prod,
            tutor="Alice",
            course=Group.CourseChoices.JUNIOR_MATHS,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day="10:00:00"
        )

        # 3. Create a Lesson under that Group
        self.lesson = Lesson.objects.create(
            group=self.group,
            notes="Algebra intro"
        )

        # 4. Create a Parent (basket auto-created by signal)
        self.parent = Parent.objects.create(
            name="Mr Smith",
            stripeId="cus_test123"
        )

        # 5. Create TutoringStudent assigned to group + parent
        self.student = TutoringStudent.objects.create(
            name="John Doe",
            parent=self.parent
        )
        self.student.group.add(self.group)

        # 6. API URL
        self.url = reverse("bulkAddAttendances")

    def test_bulk_create_single_attendance(self):
        data = [
            {
                "lesson": self.lesson.id,
                "tutoringStudent": self.student.id,
                "homework": True,
                "paid": False
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["homework"], True)

    def test_bulk_create_multiple_attendances(self):
        student2 = TutoringStudent.objects.create(name="Jane Doe", parent=self.parent)
        data = [
            {
                "lesson": self.lesson.id,
                "tutoringStudent": self.student.id,
                "homework": False,
                "paid": True
            },
            {
                "lesson": self.lesson.id,
                "tutoringStudent": student2.id,
                "homework": True,
                "paid": True
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_invalid_bulk_create_missing_field(self):
        data = [
            {
                "lesson": self.lesson.id,
                # tutoringStudent missing!
                "homework": False,
                "paid": False
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # serializer errors returned
        self.assertIn("tutoringStudent", response.data[0])
