from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from tutoring.models import Group, Lesson, TutoringStudent, TutoringTerm, TutoringWeek
import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set term lessons for groups'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='Monday of the first week (YYYY-MM-DD)')
        parser.add_argument('--term_id', type=int, help='ID of the tutoring term (optional)')
        parser.add_argument('--student_id', type=int, help='ID of student enrolling mid-term (only schedules remaining weeks)')

    def handle(self, *args, **options):
        start_date = options['start_date']
        term_id = options.get('term_id')
        student_id = options.get('student_id')
        
        try:
            first_monday = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Validate that the start_date is actually a Monday
            if first_monday.weekday() != 0:  # 0 = Monday
                raise CommandError(f'{start_date} is not a Monday. Please provide a Monday date.')
            
            if term_id:
                term = TutoringTerm.objects.get(id=term_id)
            else:
                # Get the current/latest term if not specified
                term = TutoringTerm.objects.latest('id')
            
            # Update the term's start_date and recalculate week dates
            if not term.start_date or term.start_date != first_monday:
                week_count = term.update_week_dates(first_monday)
                self.stdout.write(self.style.SUCCESS(f"Updated {week_count} weeks for {term}"))
            
            if student_id:
                student = TutoringStudent.objects.get(id=student_id)
                scheduleTermLessonsForStudent(term, first_monday, student)
                self.stdout.write(self.style.SUCCESS(f"Lessons scheduled for {student.name} in term {term} (remaining weeks only)"))
            else:
                scheduleTermLessons(term, first_monday)
                self.stdout.write(self.style.SUCCESS(f"Lessons scheduled for term {term} starting {first_monday}"))
            
        except TutoringTerm.DoesNotExist:
            raise CommandError(f'Term with ID {term_id} not found')
        except TutoringStudent.DoesNotExist:
            raise CommandError(f'Student with ID {student_id} not found')
        except Exception as e:
            raise CommandError(f'Command failed: {e}')


# def _update_week_dates(term: TutoringTerm, first_monday: datetime.date):
#     """
#     Update all weeks in the term with their monday_date and sunday_date.
    
#     :param term: TutoringTerm object
#     :param first_monday: datetime.date of the first Monday of the term
#     """
#     weeks = term.weeks.all().order_by('index')
    
#     for i, week in enumerate(weeks):
#         monday = first_monday + timedelta(weeks=i)
#         sunday = monday + timedelta(days=6)
        
#         week.monday_date = monday
#         week.sunday_date = sunday
#         week.save()
        
#         logger.debug(f"Updated {week} with dates {monday} to {sunday}")
    
#     logger.info(f"Updated date ranges for {weeks.count()} weeks in {term}")


def scheduleTermLessons(term: TutoringTerm, first_monday: datetime.date):
    """
    Creates lessons for every group for the given term.
    One lesson per group per week, assigned to the correct TutoringWeek.

    :param term: TutoringTerm object
    :param first_monday: datetime.date of the first Monday of the term
    """
    groups = Group.objects.all()
    weeks = term.weeks.all().order_by('index')  # Get all weeks for this term
    
    if not weeks.exists():
        logger.error(f"Term {term} has no weeks defined")
        return
    
    for group in groups:
        # Calculate the first lesson date for the group
        days_until_group_day = (group.day_of_week - first_monday.weekday()) % 7
        first_lesson_date = datetime.combine(
            first_monday + timedelta(days=days_until_group_day), 
            group.time_of_day
        )
        
        # Create one lesson per week
        for i, week in enumerate(weeks):
            lesson_date = first_lesson_date + timedelta(weeks=i)
            
            Lesson.objects.create(
                group=group,
                date=lesson_date,
                tutoringWeek=week
            )
            
            logger.debug(f"Created lesson for {group} in {week} on {lesson_date}")
        
        logger.info(f"Scheduled {weeks.count()} lessons for {group} in term {term}")


def scheduleTermLessonsForStudent(term: TutoringTerm, first_monday: datetime.date, student):
    """
    Creates lessons for a student's groups for remaining weeks in the term.
    Used when a student enrolls mid-term.

    :param term: TutoringTerm object
    :param first_monday: datetime.date of the first Monday of the term
    :param student: TutoringStudent object to enroll
    """
    # Get the groups this student is enrolled in
    groups = student.group.all()
    
    if not groups.exists():
        logger.warning(f"Student {student.name} is not enrolled in any groups")
        return
    
    weeks = term.weeks.all().order_by('index')
    
    if not weeks.exists():
        logger.error(f"Term {term} has no weeks defined")
        return
    
    # Determine which week we're currently in based on today's date
    today = datetime.now().date()
    current_week = None
    
    for week in weeks:
        if week.monday_date <= today <= week.sunday_date:
            current_week = week
            break
        elif today < week.monday_date:
            # We're before this week starts, so start from this week
            current_week = week
            break
    
    # If we didn't find a current week, check if we're past the term
    if current_week is None:
        if today > weeks.last().sunday_date:
            logger.warning(f"Cannot enroll {student.name}: term has already ended")
            return
        # Otherwise, start from the first week
        current_week = weeks.first()
    
    # Get weeks from current onwards
    remaining_weeks = weeks.filter(index__gte=current_week.index)
    
    logger.info(f"Student {student.name} enrolling at week {current_week.index}, {remaining_weeks.count()} weeks remaining")
    
    for group in groups:
        # Calculate the first lesson date for the group
        days_until_group_day = (group.day_of_week - first_monday.weekday()) % 7
        first_lesson_date = datetime.combine(
            first_monday + timedelta(days=days_until_group_day), 
            group.time_of_day
        )
        
        # Create lessons for remaining weeks only
        for week in remaining_weeks:
            # Calculate which week number this is (0-indexed from start of term)
            week_offset = week.index - 1
            lesson_date = first_lesson_date + timedelta(weeks=week_offset)
            
            lesson, created = Lesson.objects.get_or_create(
                group=group,
                date=lesson_date,
                tutoringWeek=week
            )
            
            if created:
                logger.debug(f"Created lesson for {student.name} in {group} for {week} on {lesson_date}")
            else:
                logger.debug(f"Lesson already exists for {group} in {week}")
        
        logger.info(f"Scheduled {remaining_weeks.count()} lessons for {student.name} in {group} (weeks {current_week.index}-{weeks.last().index})")