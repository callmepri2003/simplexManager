from datetime import datetime, time, timedelta
import zoneinfo
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from unittest.mock import patch

from tutoring.models import Group, Lesson, TutoringTerm, TutoringYear, TutoringWeek, TutoringStudent, Parent, Attendance


class ScheduleTermLessonsTest(TestCase):
    """Tests for full-term lesson scheduling"""
    
    def setUp(self):
        """Create test groups with different days and times"""
        self.year = TutoringYear.objects.create(index=2024)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)
        
        self.monday_group = Group.objects.create(
            tutor="John",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            lesson_length=1,
            time_of_day=time(14, 0)
        )
        self.wednesday_group = Group.objects.create(
            tutor="Sarah",
            course=Group.CourseChoices.YEAR12_EXT1,
            day_of_week=Group.Weekday.WEDNESDAY,
            lesson_length=1,
            time_of_day=time(15, 30)
        )
        self.friday_group = Group.objects.create(
            tutor="Mike",
            course=Group.CourseChoices.YEAR12_ADV,
            day_of_week=Group.Weekday.FRIDAY,
            lesson_length=2,
            time_of_day=time(16, 0)
        )
    
    def test_creates_lessons_for_all_groups(self):
        """Test that 10 lessons are created for each group"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        self.assertEqual(Lesson.objects.filter(group=self.monday_group).count(), 10)
        self.assertEqual(Lesson.objects.filter(group=self.wednesday_group).count(), 10)
        self.assertEqual(Lesson.objects.filter(group=self.friday_group).count(), 10)
    
    def test_first_lesson_on_correct_day(self):
        """Test that first lesson starts on the correct day of week"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        # Monday group starts on March 4 (Monday)
        first_monday_lesson = Lesson.objects.filter(group=self.monday_group).earliest('date')
        self.assertEqual(first_monday_lesson.date.date(), datetime(2024, 3, 4).date())
        
        # Wednesday group starts on March 6 (Wednesday)
        first_wednesday_lesson = Lesson.objects.filter(group=self.wednesday_group).earliest('date')
        self.assertEqual(first_wednesday_lesson.date.date(), datetime(2024, 3, 6).date())
        
        # Friday group starts on March 8 (Friday)
        first_friday_lesson = Lesson.objects.filter(group=self.friday_group).earliest('date')
        self.assertEqual(first_friday_lesson.date.date(), datetime(2024, 3, 8).date())
    
    def test_lessons_are_weekly(self):
        """Test that lessons are scheduled 7 days apart"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        lessons = Lesson.objects.filter(group=self.monday_group).order_by('date')
        
        for i in range(len(lessons) - 1):
            days_diff = (lessons[i + 1].date - lessons[i].date).days
            self.assertEqual(days_diff, 7)
    
    def test_lessons_preserve_time(self):
        """Test that all lessons maintain their group's time of day"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        # Get Sydney timezone
        local_tz = zoneinfo.ZoneInfo('Australia/Sydney')
        
        for lesson in Lesson.objects.filter(group=self.monday_group):
            local_time = lesson.date.astimezone(local_tz).time()
            self.assertEqual(local_time, time(14, 0))
        
        for lesson in Lesson.objects.filter(group=self.wednesday_group):
            local_time = lesson.date.astimezone(local_tz).time()
            self.assertEqual(local_time, time(15, 30))
    
    def test_lessons_assigned_to_correct_weeks(self):
        """Test that lessons are assigned to the correct TutoringWeek"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        lessons = Lesson.objects.filter(group=self.monday_group).order_by('date')
        
        for i, lesson in enumerate(lessons):
            expected_week_index = i + 1
            self.assertEqual(lesson.tutoringWeek.index, expected_week_index)
            self.assertEqual(lesson.tutoringWeek.term, self.term)
    
    def test_term_has_10_weeks_by_default(self):
        """Test that new term auto-creates 10 weeks"""
        weeks = self.term.weeks.all()
        self.assertEqual(weeks.count(), 10)
        
        for i, week in enumerate(weeks.order_by('index')):
            self.assertEqual(week.index, i + 1)
    
    def test_only_one_lesson_per_group_per_week(self):
        """Test that there's exactly one lesson per group per week"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        weeks = self.term.weeks.all()
        
        for group in [self.monday_group, self.wednesday_group, self.friday_group]:
            for week in weeks:
                lessons_in_week = Lesson.objects.filter(group=group, tutoringWeek=week)
                self.assertEqual(
                    lessons_in_week.count(), 
                    1, 
                    f"Expected 1 lesson for {group} in {week}, got {lessons_in_week.count()}"
                )
    
    def test_creates_attendance_records_for_all_students(self):
        """Test that attendance records are created when lessons are created"""
        # Create students and enroll them
        parent = Parent.objects.create(name="Test Parent", stripeId="cus_test")
        student1 = TutoringStudent.objects.create(name="Student 1", parent=parent)
        student2 = TutoringStudent.objects.create(name="Student 2", parent=parent)
        
        student1.group.add(self.monday_group)
        student2.group.add(self.monday_group)
        
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        # Check attendance records
        lessons = Lesson.objects.filter(group=self.monday_group)
        for lesson in lessons:
            attendances = lesson.attendances.all()
            self.assertEqual(attendances.count(), 2)
            
            attending_students = set(a.tutoringStudent.id for a in attendances)
            self.assertEqual(attending_students, {student1.id, student2.id})
    
    def test_week_dates_set_correctly(self):
        """Test that TutoringWeek monday_date and sunday_date are set correctly"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        weeks = self.term.weeks.all().order_by('index')
        
        for i, week in enumerate(weeks):
            expected_monday = datetime(2024, 3, 4).date() + timedelta(weeks=i)
            expected_sunday = expected_monday + timedelta(days=6)
            
            self.assertEqual(week.monday_date, expected_monday)
            self.assertEqual(week.sunday_date, expected_sunday)
    
    def test_can_query_week_by_date(self):
        """Test that we can query which week a specific date falls in"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        # March 6, 2024 is a Wednesday in the first week
        test_date = datetime(2024, 3, 6).date()
        week = TutoringWeek.objects.get(
            monday_date__lte=test_date,
            sunday_date__gte=test_date,
            term=self.term
        )
        
        self.assertEqual(week.index, 1)
        
        # March 13, 2024 is a Wednesday in the second week
        test_date2 = datetime(2024, 3, 13).date()
        week2 = TutoringWeek.objects.get(
            monday_date__lte=test_date2,
            sunday_date__gte=test_date2,
            term=self.term
        )
        
        self.assertEqual(week2.index, 2)
    
    def test_start_date_must_be_monday(self):
        """Test that command fails if start_date is not a Monday"""
        # March 5, 2024 is a Tuesday
        with self.assertRaises(CommandError) as cm:
            call_command('set_term', '2024-03-05', '--term_id', str(self.term.id))
        
        self.assertIn('not a Monday', str(cm.exception))


class ScheduleMidTermEnrollmentTest(TestCase):
    """Tests for mid-term student enrollment"""
    
    def setUp(self):
        """Create a term with lessons already scheduled"""
        self.year = TutoringYear.objects.create(index=2024)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)
        
        self.group = Group.objects.create(
            tutor="John",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            lesson_length=1,
            time_of_day=time(14, 0)
        )
        
        # Schedule full term starting March 4 (Monday)
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        # Create a student
        parent = Parent.objects.create(name="Test Parent", stripeId="cus_test")
        self.student = TutoringStudent.objects.create(name="Late Enrollee", parent=parent)
        self.student.group.add(self.group)
    
    def test_mid_term_enrollment_creates_attendance_records(self):
        """Test that mid-term enrollment creates attendance records for the student"""
        # Mock today as being in week 5 (March 31, 2024 - Sunday of week 5)
        with patch('tutoring.management.commands.set_term.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 31, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id), 
                        '--student_id', str(self.student.id))
        
        # Should create attendance for weeks 5-10 (6 weeks)
        attendances = Attendance.objects.filter(tutoringStudent=self.student)
        self.assertEqual(attendances.count(), 6)
    
    def test_mid_term_enrollment_starts_from_current_week(self):
        """Test that mid-term enrollment starts from the current week"""
        # Mock today as being in week 3 (March 18, 2024 - Monday of week 3)
        with patch('tutoring.management.commands.set_term.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 18, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', str(self.student.id))
        
        attendances = Attendance.objects.filter(tutoringStudent=self.student)
        # Should create attendance for weeks 3-10 (8 weeks)
        self.assertEqual(attendances.count(), 8)
        
        # Verify they're for the correct weeks
        week_indices = set(a.lesson.tutoringWeek.index for a in attendances)
        expected_weeks = set(range(3, 11))  # weeks 3-10
        self.assertEqual(week_indices, expected_weeks)
    
    def test_mid_term_enrollment_before_term_starts(self):
        """Test enrollment before term starts includes all weeks"""
        # Mock today as being before term (March 1, 2024)
        with patch('tutoring.management.commands.set_term.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 1, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', str(self.student.id))
        
        attendances = Attendance.objects.filter(tutoringStudent=self.student)
        # Should create attendance for all 10 weeks
        self.assertEqual(attendances.count(), 10)
    
    def test_mid_term_enrollment_after_term_ends(self):
        """Test that enrollment after term ends is handled gracefully"""
        # Mock today as being after term (May 20, 2024)
        with patch('tutoring.management.commands.set_term.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 5, 20, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', str(self.student.id))
        
        # Should create no attendance records
        attendances = Attendance.objects.filter(tutoringStudent=self.student)
        self.assertEqual(attendances.count(), 0)
    
    def test_mid_term_enrollment_idempotent(self):
        """Test that running mid-term enrollment twice doesn't duplicate lessons"""
        with patch('tutoring.management.commands.set_term.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 18, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', str(self.student.id))
            first_count = Attendance.objects.filter(tutoringStudent=self.student).count()
            
            # Run again
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', str(self.student.id))
            second_count = Attendance.objects.filter(tutoringStudent=self.student).count()
        
        # Should be same (idempotent)
        self.assertEqual(first_count, second_count)
    
    def test_mid_term_enrollment_multiple_groups(self):
        """Test that mid-term enrollment works for students in multiple groups"""
        group2 = Group.objects.create(
            tutor="Sarah",
            course=Group.CourseChoices.YEAR12_EXT1,
            day_of_week=Group.Weekday.WEDNESDAY,
            lesson_length=1,
            time_of_day=time(15, 30)
        )
        
        # Schedule lessons for the new group
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        self.student.group.add(group2)
        
        # Mock today as being in week 2 (March 11, 2024)
        with patch('tutoring.management.commands.set_term.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 11, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', str(self.student.id))
        
        attendances = Attendance.objects.filter(tutoringStudent=self.student)
        # Should have 9 weeks × 2 groups = 18 attendances (weeks 2-10)
        self.assertEqual(attendances.count(), 18)
    
    def test_mid_term_enrollment_nonexistent_student(self):
        """Test that command fails gracefully for nonexistent student"""
        with self.assertRaises(CommandError):
            call_command('set_term', '2024-03-04', '--term_id', str(self.term.id),
                        '--student_id', '9999')


class ScheduleLessonsEdgeCasesTest(TestCase):
    """Tests for edge cases and error handling"""
    
    def setUp(self):
        """Create basic test data"""
        self.year = TutoringYear.objects.create(index=2024)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)
    
    def test_no_groups_schedules_nothing(self):
        """Test that scheduling with no groups creates no lessons"""
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        self.assertEqual(Lesson.objects.count(), 0)
    
    def test_multiple_terms_independent(self):
        """Test that lessons in different terms are independent"""
        year2 = TutoringYear.objects.create(index=2025)
        term2 = TutoringTerm.objects.create(index=1, year=year2)
        
        group = Group.objects.create(
            tutor="John",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            lesson_length=1,
            time_of_day=time(14, 0)
        )
        
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        call_command('set_term', '2025-03-03', '--term_id', str(term2.id))
        
        term1_lessons = Lesson.objects.filter(tutoringWeek__term=self.term).count()
        term2_lessons = Lesson.objects.filter(tutoringWeek__term=term2).count()
        
        self.assertEqual(term1_lessons, 10)
        self.assertEqual(term2_lessons, 10)
        self.assertEqual(Lesson.objects.count(), 20)
    
    def test_nonexistent_term(self):
        """Test that command fails gracefully for nonexistent term"""
        with self.assertRaises(CommandError):
            call_command('set_term', '2024-03-04', '--term_id', '9999')
    
    def test_start_date_required(self):
        """Test that start_date is required"""
        with self.assertRaises(CommandError):
            call_command('set_term', '--term_id', str(self.term.id))
    
    def test_lessons_respect_lesson_length(self):
        """Test that lessons are created with correct lesson_length (affects invoicing)"""
        group = Group.objects.create(
            tutor="John",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            lesson_length=2,  # 2-hour lessons
            time_of_day=time(14, 0)
        )
        
        call_command('set_term', '2024-03-04', '--term_id', str(self.term.id))
        
        # All lessons should be for the same group with same length
        lessons = Lesson.objects.filter(group=group)
        for lesson in lessons:
            self.assertEqual(lesson.group.lesson_length, 2)