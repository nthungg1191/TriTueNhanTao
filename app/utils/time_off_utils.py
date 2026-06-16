"""Utility functions for time-off and overtime validation (pure functions for unit tests)."""
from datetime import date, timedelta


def is_valid_leave_range(start_date: date, end_date: date) -> bool:
    """Return True if start_date <= end_date."""
    if start_date is None or end_date is None:
        return False
    return start_date <= end_date


def is_valid_overtime_hours(hours: float) -> bool:
    """Return True if hours is a positive number (greater than 0)."""
    try:
        return float(hours) > 0
    except Exception:
        return False


def is_at_least_days_ahead(target_date: date, reference_date: date | None = None, minimum_days: int = 3) -> bool:
    """Return True if target_date is at least minimum_days after reference_date."""
    if target_date is None:
        return False

    if reference_date is None:
        reference_date = date.today()

    try:
        minimum_days = int(minimum_days)
    except Exception:
        return False

    return target_date >= reference_date + timedelta(days=minimum_days)


def ranges_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    """Return True if two closed date ranges overlap."""
    if a_start is None or a_end is None or b_start is None or b_end is None:
        return False
    return not (a_end < b_start or b_end < a_start)
