import re
from rest_framework.exceptions import ValidationError
from tutoring.models import TutoringYear, TutoringTerm

def parse_term(term_str):
    """
    Parse a term string like '24T3' into a dictionary with year and term.
    """
    pattern = r'^(?P<year>\d{2})T(?P<term>\d)$'
    match = re.match(pattern, term_str, re.IGNORECASE)
    if not match:
        raise ValidationError({
            "term": "Invalid term format. Expected format like '24T3'."
        })
    return {
        "year": int(match.group('year')),
        "term": int(match.group('term')),
    }

def validate_term_format(term_str, field_name="term"):
    """
    Validate the term string format like '24T3' and raise ValidationError if invalid.
    """
    pattern = r'^\d{2}T\d$'
    if not re.match(pattern, term_str or '', re.IGNORECASE):
        raise ValidationError({
            field_name: f"Invalid {field_name} format. Expected format like '24T3'."
        })

def fetch_term(term_dict):
    """
    Fetch a single TutoringTerm object based on parsed term dict.
    Raises ValidationError if year/term does not exist.
    """
    try:
        year_obj = TutoringYear.objects.get(index=term_dict['year'])
    except TutoringYear.DoesNotExist:
        raise ValidationError({"Ranges": "One or more of the ranges don't exist"})

    try:
        term_obj = TutoringTerm.objects.get(index=term_dict['term'], year=year_obj)
    except TutoringTerm.DoesNotExist:
        raise ValidationError({"Ranges": "One or more of the ranges don't exist"})

    return term_obj

def collateAnalyticsAmountOfEnrolments(term_obj):
    """
    Returns analytics for a given term:
        - amountOfEnrolments: int
        - change: float (None if no previous term)
        - trend: '+' or '-' (None if no previous term)
    """
    # Current term enrolments
    current_count = term_obj.amountOfEnrolments()

    # Previous term enrolments
    prev_term_obj = getattr(term_obj, "previousTerm", None)
    if prev_term_obj:
        prev_count = prev_term_obj.amountOfEnrolments()
        # Avoid division by zero
        if prev_count:
            percentage_change = ((current_count - prev_count) / prev_count) * 100
        else:
            percentage_change = 100.0 if current_count > 0 else 0.0
        trend = '+' if current_count >= prev_count else '-'
    else:
        percentage_change = None
        trend = None

    return {
        "amountOfEnrolments": current_count,
        "change": percentage_change,
        "trend": trend
    }