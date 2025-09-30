import datetime
import json
from pathlib import Path
from rest_framework.test import APITestCase
from stripeInt.models import StripeProd
from tutoring.models import Group, Lesson, Parent, TutoringStudent
from rest_framework import status
from django.urls import reverse

def strip_ids(obj):
    """
    Recursively remove any 'id' fields from dicts/lists.
    """
    if isinstance(obj, dict):
        return {k: strip_ids(v) for k, v in obj.items() if k != "id"}
    elif isinstance(obj, list):
        return [strip_ids(i) for i in obj]
    return obj


class GroupApiTest(APITestCase):

    def setUp(self):
        prod = StripeProd.objects.create(
            stripeId="prod_test123",
            defaultPriceId="price_test123",
            name="Tutoring Product",
            is_active=True
        )

        Group.objects.create(
            lesson_length=1,
            associated_product=prod,
            tutor="Alice",
            course=Group.CourseChoices.JUNIOR_MATHS,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day=datetime.time(16, 0)
        )
        Group.objects.create(
            lesson_length=2,
            associated_product=prod,
            tutor="Bob",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.WEDNESDAY,
            time_of_day=datetime.time(18, 30)
        )
        Group.objects.create(
            lesson_length=1,
            associated_product=prod,
            tutor="Charlie",
            course=Group.CourseChoices.YEAR12_EXT1,
            day_of_week=Group.Weekday.SATURDAY,
            time_of_day=datetime.time(10, 0)
        )

    def test_list_all_groups(self):
        actual = self.client.get('/api/groups/').data
        expected = json.loads(
            (Path(__file__).parent / "fixtures/GroupApiTest/test_list_all_groups.json").read_text()
        )

        # normalize by stripping IDs
        actual_clean = strip_ids(actual)
        expected_clean = strip_ids(expected)

        # sort by tutor for consistency
        actual_sorted = sorted(actual_clean, key=lambda g: g["tutor"])
        expected_sorted = sorted(expected_clean, key=lambda g: g["tutor"])

        self.assertEqual(actual_sorted, expected_sorted)



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
            notes="Algebra intro",
            date='2024-01-15'
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # serializer errors returned
        self.assertIn("tutoringStudent", response.data[0])

class DeleteLessons(APITestCase):
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
            notes="Algebra intro",
            date='2024-01-15'
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
        self.url = reverse("getEditDeleteLessons", kwargs={
            'pk': self.lesson.pk
        })

    def testDeleteBasic(self):
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def testDeleteNotFound(self):
        non_existent_pk = 99999
        url = reverse("getEditDeleteLessons", kwargs={'pk': non_existent_pk})
        
        response = self.client.delete(url, format="json")
        
        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data['error'], 'Item not found')