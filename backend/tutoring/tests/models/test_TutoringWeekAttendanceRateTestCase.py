from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from tutoring.models import (
    TutoringWeek, TutoringTerm, TutoringYear, 
    Group, Lesson, Attendance, TutoringStudent, 
    Parent, LocalInvoice
)

from stripeInt.models import StripeProd

from api.utils import collateAnalyticsAttendanceRate

class TutoringWeekAttendanceRateTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.year = TutoringYear.objects.create(index=2025)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)
        self.week1 = self.term.weeks.get(index=1)
        self.week2 = self.term.weeks.get(index=2)
        
        self.product = StripeProd.objects.create(
            stripeId='prod_test123',
            name='Test Product',
            defaultPriceId='price_test123'
        )
        
        self.group = Group.objects.create(
            lesson_length=90,
            tutor='Test Tutor',
            course='12 Advanced',
            day_of_week=0,
            associated_product=self.product
        )
        
        self.parent = Parent.objects.create(
            name='Test Parent',
            stripeId='cus_test123'
        )
        
        self.student1 = TutoringStudent.objects.create(
            name='Student 1',
            parent=self.parent,
            active=True
        )
        self.student1.group.add(self.group)
        
        self.student2 = TutoringStudent.objects.create(
            name='Student 2',
            parent=self.parent,
            active=True
        )
        self.student2.group.add(self.group)
        
        self.student3 = TutoringStudent.objects.create(
            name='Student 3',
            parent=self.parent,
            active=True
        )
        self.student3.group.add(self.group)
    
    def test_week_attendance_rate_no_lessons(self):
        """Test attendance rate when there are no lessons"""
        rate = self.week1.get_attendance_rate()
        self.assertEqual(rate, 0.0)
    
    def test_week_attendance_rate_all_present(self):
        """Test attendance rate when all students are present"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Update the auto-created attendance records
        lesson.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson.attendances.filter(tutoringStudent=self.student2).update(present=True)
        lesson.attendances.filter(tutoringStudent=self.student3).update(present=True)
        
        rate = self.week1.get_attendance_rate()
        self.assertEqual(rate, 100.0)
    
    def test_week_attendance_rate_none_present(self):
        """Test attendance rate when no students are present"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Attendances are already False by default, but let's be explicit
        lesson.attendances.update(present=False)
        
        rate = self.week1.get_attendance_rate()
        self.assertEqual(rate, 0.0)
    
    def test_week_attendance_rate_partial(self):
        """Test attendance rate with partial attendance"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Update the auto-created attendance records
        lesson.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson.attendances.filter(tutoringStudent=self.student2).update(present=False)
        lesson.attendances.filter(tutoringStudent=self.student3).update(present=True)
        
        rate = self.week1.get_attendance_rate()
        self.assertAlmostEqual(rate, 66.666667, places=5)
    
    def test_week_attendance_rate_multiple_lessons(self):
        """Test attendance rate across multiple lessons in the same week"""
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=1),
            tutoringWeek=self.week1
        )
        
        # Lesson 1: 2/3 present
        lesson1.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson1.attendances.filter(tutoringStudent=self.student2).update(present=False)
        lesson1.attendances.filter(tutoringStudent=self.student3).update(present=True)
        
        # Lesson 2: 1/3 present
        lesson2.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson2.attendances.filter(tutoringStudent=self.student2).update(present=False)
        lesson2.attendances.filter(tutoringStudent=self.student3).update(present=False)
        
        # Overall: 3/6 = 50%
        rate = self.week1.get_attendance_rate()
        self.assertEqual(rate, 50.0)


class TutoringTermAttendanceRateTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.year = TutoringYear.objects.create(index=2025)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)
        
        self.product = StripeProd.objects.create(
            stripeId='prod_test123',
            name='Test Product',
            defaultPriceId='price_test123'
        )
        
        self.group = Group.objects.create(
            lesson_length=90,
            tutor='Test Tutor',
            course='12 Advanced',
            day_of_week=0,
            associated_product=self.product
        )
        
        self.parent = Parent.objects.create(
            name='Test Parent',
            stripeId='cus_test123'
        )
        
        self.student1 = TutoringStudent.objects.create(
            name='Student 1',
            parent=self.parent,
            active=True
        )
        self.student1.group.add(self.group)
        
        self.student2 = TutoringStudent.objects.create(
            name='Student 2',
            parent=self.parent,
            active=True
        )
        self.student2.group.add(self.group)
    
    def test_term_attendance_rate_no_data(self):
        """Test term attendance rate when there's no attendance data"""
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 0.0)
    
    def test_term_attendance_rate_single_week(self):
        """Test term attendance rate with data in one week"""
        week1 = self.term.weeks.get(index=1)
        
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        
        # Update the auto-created attendance records
        lesson.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson.attendances.filter(tutoringStudent=self.student2).update(present=False)
        
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 50.0)
    
    def test_term_attendance_rate_multiple_weeks(self):
        """Test term attendance rate averaging across multiple weeks"""
        week1 = self.term.weeks.get(index=1)
        week2 = self.term.weeks.get(index=2)
        week3 = self.term.weeks.get(index=3)
        
        # Week 1: 100% attendance
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        lesson1.attendances.update(present=True)
        
        # Week 2: 50% attendance
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=week2
        )
        lesson2.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson2.attendances.filter(tutoringStudent=self.student2).update(present=False)
        
        # Week 3: 0% attendance
        lesson3 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=14),
            tutoringWeek=week3
        )
        lesson3.attendances.update(present=False)
        
        # Average: (100 + 50 + 0) / 3 = 50%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 50.0)
    
    def test_term_attendance_rate_only_counts_weeks_with_data(self):
        """Test that term average only includes weeks with attendance data"""
        week1 = self.term.weeks.get(index=1)
        week2 = self.term.weeks.get(index=2)
        # weeks 3-10 have no data
        
        # Week 1: 100%
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        lesson1.attendances.update(present=True)
        
        # Week 2: 50%
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=week2
        )
        lesson2.attendances.filter(tutoringStudent=self.student1).update(present=True)
        lesson2.attendances.filter(tutoringStudent=self.student2).update(present=False)
        
        # Should average only weeks 1 and 2: (100 + 50) / 2 = 75%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 75.0)
    
    def test_term_attendance_rate_with_varied_rates(self):
        """Test term attendance rate with more varied week rates"""
        week1 = self.term.weeks.get(index=1)
        week2 = self.term.weeks.get(index=2)
        week3 = self.term.weeks.get(index=3)
        week4 = self.term.weeks.get(index=4)
        
        # Week 1: 100% (2/2)
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        lesson1.attendances.update(present=True)
        
        # Week 2: 50% (1/2)
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=week2
        )
        lesson2.attendances.filter(tutoringStudent=self.student1).update(present=True)
        
        # Week 3: 0% (0/2)
        lesson3 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=14),
            tutoringWeek=week3
        )
        lesson3.attendances.update(present=False)
        
        # Week 4: 100% (2/2)
        lesson4 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=21),
            tutoringWeek=week4
        )
        lesson4.attendances.update(present=True)
        
        # Average: (100 + 50 + 0 + 100) / 4 = 62.5%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 62.5)
    
    def test_term_attendance_rate_with_multiple_lessons_per_week(self):
        """Test term correctly averages weeks that have multiple lessons"""
        week1 = self.term.weeks.get(index=1)
        week2 = self.term.weeks.get(index=2)
        
        # Week 1: Two lessons
        # Lesson 1: 100% (2/2)
        lesson1a = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        lesson1a.attendances.update(present=True)
        
        # Lesson 2: 50% (1/2)
        lesson1b = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(hours=2),
            tutoringWeek=week1
        )
        lesson1b.attendances.filter(tutoringStudent=self.student1).update(present=True)
        
        # Week 1 average: (2 + 1) / 4 = 75%
        
        # Week 2: One lesson at 100% (2/2)
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=week2
        )
        lesson2.attendances.update(present=True)
        
        # Week 2 average: 100%
        
        # Term average: (75 + 100) / 2 = 87.5%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 87.5)
    
    def test_term_attendance_rate_all_weeks_perfect(self):
        """Test term with perfect attendance across all weeks"""
        for week_index in range(1, 6):
            week = self.term.weeks.get(index=week_index)
            lesson = Lesson.objects.create(
                group=self.group,
                date=timezone.now() + timedelta(days=(week_index - 1) * 7),
                tutoringWeek=week
            )
            lesson.attendances.update(present=True)
        
        # All weeks at 100%, average should be 100%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 100.0)
    
    def test_term_attendance_rate_all_weeks_zero(self):
        """Test term with zero attendance across all weeks"""
        for week_index in range(1, 6):
            week = self.term.weeks.get(index=week_index)
            lesson = Lesson.objects.create(
                group=self.group,
                date=timezone.now() + timedelta(days=(week_index - 1) * 7),
                tutoringWeek=week
            )
            lesson.attendances.update(present=False)
        
        # All weeks at 0%, average should be 0%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 0.0)
    
    def test_term_attendance_rate_sparse_weeks(self):
        """Test term with data only in non-consecutive weeks"""
        week1 = self.term.weeks.get(index=1)
        week5 = self.term.weeks.get(index=5)
        week9 = self.term.weeks.get(index=9)
        
        # Week 1: 100%
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        lesson1.attendances.update(present=True)
        
        # Weeks 2-4: no data (shouldn't count)
        
        # Week 5: 50%
        lesson5 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=28),
            tutoringWeek=week5
        )
        lesson5.attendances.filter(tutoringStudent=self.student1).update(present=True)
        
        # Weeks 6-8: no data (shouldn't count)
        
        # Week 9: 0%
        lesson9 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=56),
            tutoringWeek=week9
        )
        lesson9.attendances.update(present=False)
        
        # Average only weeks with data: (100 + 50 + 0) / 3 = 50%
        rate = self.term.get_attendance_rate()
        self.assertEqual(rate, 50.0)


class CollateAnalyticsAttendanceRateTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.year = TutoringYear.objects.create(index=2025)
        
        self.product = StripeProd.objects.create(
            stripeId='prod_test123',
            name='Test Product',
            defaultPriceId='price_test123'
        )
        
        self.parent = Parent.objects.create(
            name='Test Parent',
            stripeId='cus_test123'
        )
        
        # Create a pool of students that we can reuse
        self.student_pool = []
        for i in range(1, 21):  # Create 20 students
            student = TutoringStudent.objects.create(
                name=f'Student {i}',
                parent=self.parent,
                active=True
            )
            self.student_pool.append(student)
    
    def _add_attendance_to_week(self, week, present_count, absent_count):
        """Helper to add attendance data to a week"""
        total_needed = present_count + absent_count
        
        # Create a fresh group for this lesson with the exact number of students needed
        group = Group.objects.create(
            lesson_length=90,
            tutor='Test Tutor',
            course='12 Advanced',
            day_of_week=0,
            associated_product=self.product
        )
        
        # Add the required number of students to this group
        for i in range(total_needed):
            self.student_pool[i].group.add(group)
        
        # NOW create the lesson - the signal will create attendance for all students in the group
        lesson = Lesson.objects.create(
            group=group,
            date=timezone.now(),
            tutoringWeek=week
        )
        
        # Update attendance records - first N are present, rest are absent
        all_attendances = list(lesson.attendances.all())
        for i in range(present_count):
            all_attendances[i].present = True
            all_attendances[i].save()
    
    def test_collate_no_previous_term(self):
        """Test collate analytics when there's no previous term"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        week1 = term1.weeks.get(index=1)
        
        self._add_attendance_to_week(week1, present_count=8, absent_count=2)
        
        result = collateAnalyticsAttendanceRate(term1)
        
        self.assertEqual(result['attendanceRate'], 80.0)
        self.assertIsNone(result['change'])
        self.assertIsNone(result['trend'])
    
    def test_collate_attendance_rate_increase(self):
        """Test collate when attendance rate increased"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        # Term 1: 60% attendance
        week1_t1 = term1.weeks.get(index=1)
        self._add_attendance_to_week(week1_t1, present_count=6, absent_count=4)
        
        # Term 2: 80% attendance
        week1_t2 = term2.weeks.get(index=1)
        self._add_attendance_to_week(week1_t2, present_count=8, absent_count=2)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 80.0)
        self.assertEqual(result['change'], 20.0)  # 20 percentage point increase
        self.assertEqual(result['trend'], '+')
    
    def test_collate_attendance_rate_decrease(self):
        """Test collate when attendance rate decreased"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        # Term 1: 90% attendance
        week1_t1 = term1.weeks.get(index=1)
        self._add_attendance_to_week(week1_t1, present_count=9, absent_count=1)
        
        # Term 2: 70% attendance
        week1_t2 = term2.weeks.get(index=1)
        self._add_attendance_to_week(week1_t2, present_count=7, absent_count=3)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 70.0)
        self.assertEqual(result['change'], -20.0)  # 20 percentage point decrease
        self.assertEqual(result['trend'], '-')
    
    def test_collate_attendance_rate_no_change(self):
        """Test collate when attendance rate stayed the same"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        # Both terms: 75% attendance
        week1_t1 = term1.weeks.get(index=1)
        self._add_attendance_to_week(week1_t1, present_count=3, absent_count=1)
        
        week1_t2 = term2.weeks.get(index=1)
        self._add_attendance_to_week(week1_t2, present_count=3, absent_count=1)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 75.0)
        self.assertEqual(result['change'], 0.0)
        self.assertEqual(result['trend'], '+')  # >= means positive trend
    
    def test_collate_both_terms_zero(self):
        """Test when both terms have no attendance data"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 0.0)
        self.assertEqual(result['change'], 0.0)
        self.assertEqual(result['trend'], '+')
    
    def test_collate_multiple_weeks_averaging(self):
        """Test collate with multiple weeks of data"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        # Term 1: Week 1 = 100%, Week 2 = 50%, Average = 75%
        week1_t1 = term1.weeks.get(index=1)
        week2_t1 = term1.weeks.get(index=2)
        self._add_attendance_to_week(week1_t1, present_count=10, absent_count=0)
        self._add_attendance_to_week(week2_t1, present_count=5, absent_count=5)
        
        # Term 2: Week 1 = 80%, Week 2 = 60%, Average = 70%
        week1_t2 = term2.weeks.get(index=1)
        week2_t2 = term2.weeks.get(index=2)
        self._add_attendance_to_week(week1_t2, present_count=8, absent_count=2)
        self._add_attendance_to_week(week2_t2, present_count=6, absent_count=4)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 70.0)
        self.assertEqual(result['change'], -5.0)  # 5 percentage point decrease
        self.assertEqual(result['trend'], '-')
    
    def test_collate_chain_of_terms(self):
        """Test collate across a chain of terms"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        term3 = TutoringTerm.objects.create(index=3, year=self.year, previousTerm=term2)
        
        # Term 1: 60%
        week1_t1 = term1.weeks.get(index=1)
        self._add_attendance_to_week(week1_t1, present_count=6, absent_count=4)
        
        # Term 2: 80%
        week1_t2 = term2.weeks.get(index=1)
        self._add_attendance_to_week(week1_t2, present_count=8, absent_count=2)
        
        # Term 3: 75%
        week1_t3 = term3.weeks.get(index=1)
        self._add_attendance_to_week(week1_t3, present_count=15, absent_count=5)
        
        # Check term2 (increase from term1)
        result2 = collateAnalyticsAttendanceRate(term2)
        self.assertEqual(result2['attendanceRate'], 80.0)
        self.assertEqual(result2['change'], 20.0)
        self.assertEqual(result2['trend'], '+')
        
        # Check term3 (decrease from term2)
        result3 = collateAnalyticsAttendanceRate(term3)
        self.assertEqual(result3['attendanceRate'], 75.0)
        self.assertEqual(result3['change'], -5.0)
        self.assertEqual(result3['trend'], '-')
    
    def test_collate_previous_zero_current_has_data(self):
        """Test when previous term has no data but current term does"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        # Term 1: no data (0%)
        # Term 2: 70%
        week1_t2 = term2.weeks.get(index=1)
        self._add_attendance_to_week(week1_t2, present_count=7, absent_count=3)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 70.0)
        self.assertEqual(result['change'], 70.0)  # 70 percentage point increase from 0
        self.assertEqual(result['trend'], '+')
    
    def test_collate_current_zero_previous_has_data(self):
        """Test when current term has no data but previous term does"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        # Term 1: 85%
        week1_t1 = term1.weeks.get(index=1)
        self._add_attendance_to_week(week1_t1, present_count=17, absent_count=3)
        
        # Term 2: no data (0%)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 0.0)
        self.assertEqual(result['change'], -85.0)  # 85 percentage point decrease
        self.assertEqual(result['trend'], '-')
    
    def test_collate_with_perfect_attendance(self):
        """Test with 100% attendance in both terms"""
        term1 = TutoringTerm.objects.create(index=1, year=self.year)
        term2 = TutoringTerm.objects.create(index=2, year=self.year, previousTerm=term1)
        
        week1_t1 = term1.weeks.get(index=1)
        self._add_attendance_to_week(week1_t1, present_count=10, absent_count=0)
        
        week1_t2 = term2.weeks.get(index=1)
        self._add_attendance_to_week(week1_t2, present_count=10, absent_count=0)
        
        result = collateAnalyticsAttendanceRate(term2)
        
        self.assertEqual(result['attendanceRate'], 100.0)
        self.assertEqual(result['change'], 0.0)
        self.assertEqual(result['trend'], '+')