from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from tutoring.models import Group, Lesson


class Command(BaseCommand):
    help = 'Description of what your command does'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='Monday of the first week (YYYY-MM-DD)')
        

    def handle(self, *args, **options):
        start_date = options['start_date']
        
        try:
            # Convert string to datetime.date
            first_monday = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            scheduleTermLessons(first_monday)
            
            self.stdout.write(self.style.SUCCESS(f"Lessons scheduled starting {first_monday}"))
            
        except Exception as e:
            raise CommandError(f'Command failed: {e}')

def scheduleTermLessons(first_monday: datetime.date, term_weeks: int = 10):
    """
    Creates lessons for every group for the term, starting from the given first Monday.

    :param first_monday: datetime.date of the first Monday of the term
    :param term_weeks: Number of weeks in the term (default 10)
    """
    groups = Group.objects.all()
    
    for group in groups:
        # Calculate the first lesson date for the group
        days_until_group_day = (group.day_of_week - first_monday.weekday()) % 7
        first_lesson_date = datetime.combine(first_monday + timedelta(days=days_until_group_day), group.time_of_day)
        
        for week in range(term_weeks):
            lesson_date = first_lesson_date + timedelta(weeks=week)
            
            Lesson.objects.create(
                group=group,
                date=lesson_date
            )