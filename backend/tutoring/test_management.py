from datetime import datetime, time
import zoneinfo
from django.core.management import call_command
from django.test import TestCase

from tutoring.models import Group, Lesson


class SetTermCommandTest(TestCase):
    def setUp(self):
        """Create test groups with different days and times"""
        self.monday_group = Group.objects.create(
            tutor="John",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day=time(14, 0)
        )
        self.wednesday_group = Group.objects.create(
            tutor="Sarah",
            course=Group.CourseChoices.YEAR12_EXT1,
            day_of_week=Group.Weekday.WEDNESDAY,
            time_of_day=time(15, 30)
        )
    
    def test_creates_lessons_for_all_groups(self):
        """Test that 10 lessons are created for each group"""
        call_command('set_term', '2024-03-04')  # A Monday
        
        self.assertEqual(Lesson.objects.filter(group=self.monday_group).count(), 10)
        self.assertEqual(Lesson.objects.filter(group=self.wednesday_group).count(), 10)
    
    def test_first_lesson_on_correct_day(self):
        """Test that first lesson starts on the correct day of week"""
        call_command('set_term', '2024-03-04')  # Monday, March 4
        
        # Monday group starts on March 4
        first_monday_lesson = Lesson.objects.filter(group=self.monday_group).earliest('date')
        self.assertEqual(first_monday_lesson.date.date(), datetime(2024, 3, 4).date())
        
        # Wednesday group starts on March 6
        first_wednesday_lesson = Lesson.objects.filter(group=self.wednesday_group).earliest('date')
        self.assertEqual(first_wednesday_lesson.date.date(), datetime(2024, 3, 6).date())
    
    def test_lessons_are_weekly(self):
        """Test that lessons are scheduled 7 days apart"""
        call_command('set_term', '2024-03-04')
        
        lessons = Lesson.objects.filter(group=self.monday_group).order_by('date')
        
        for i in range(len(lessons) - 1):
            days_diff = (lessons[i + 1].date - lessons[i].date).days
            self.assertEqual(days_diff, 7)
    
    def test_lessons_preserve_time(self):
      """Test that all lessons maintain their group's time of day"""
      call_command('set_term', '2024-03-04')
      
      # Get your local timezone (Sydney)
      local_tz = zoneinfo.ZoneInfo('Australia/Sydney')
      
      for lesson in Lesson.objects.filter(group=self.monday_group):
          # Convert UTC time to local time
          local_time = lesson.date.astimezone(local_tz).time()
          self.assertEqual(local_time, time(14, 0))