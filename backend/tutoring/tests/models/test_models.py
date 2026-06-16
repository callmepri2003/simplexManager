from django.test import TestCase
from tutoring.models import (
    TutoringYear, TutoringTerm, TutoringWeek,
    Group, Lesson, TutoringStudent, Attendance, Parent
)
from datetime import datetime

class TutoringTermEnrolmentsTest(TestCase):

    def setUp(self):
        # Create a year and term
        self.year = TutoringYear.objects.create(index=2024)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)

        # Create a group
        self.group = Group.objects.create(
            lesson_length=1,
            tutor="Alice",
            course="Junior Maths",
            day_of_week=0,
            time_of_day="10:00"
        )

        # Create a parent
        self.parent = Parent.objects.create(name="Parent 1", stripeId="cus_123")

        # Create students
        self.student1 = TutoringStudent.objects.create(name="Student 1", parent=self.parent, active=True)
        self.student2 = TutoringStudent.objects.create(name="Student 2", parent=self.parent, active=True)
        self.student3 = TutoringStudent.objects.create(name="Student 3", parent=self.parent, active=True)

        # Add students to group
        self.group.tutoringStudents.add(self.student1, self.student2)

        # Create lessons
        self.lesson1 = Lesson.objects.create(group=self.group, date=datetime.now(), term=self.term)
        self.lesson2 = Lesson.objects.create(group=self.group, date=datetime.now(), term=self.term)

        # Create attendances manually for testing
        Attendance.objects.create(lesson=self.lesson1, tutoringStudent=self.student1, present=True)
        Attendance.objects.create(lesson=self.lesson1, tutoringStudent=self.student2, present=False)
        Attendance.objects.create(lesson=self.lesson2, tutoringStudent=self.student1, present=True)

    def test_amount_of_enrolments(self):
        """
        Should count unique students with at least one attendance in the term.
        In this setup: student1 and student2 have attendances → 2 unique enrolments
        """
        count = self.term.amountOfEnrolments()
        self.assertEqual(count, 2)
