from datetime import date
from app.utils.time_off_utils import is_valid_leave_range, is_valid_overtime_hours, is_at_least_days_ahead, ranges_overlap


def test_is_valid_leave_range():
    assert is_valid_leave_range(date(2026,5,1), date(2026,5,1))
    assert is_valid_leave_range(date(2026,5,1), date(2026,5,2))
    assert not is_valid_leave_range(date(2026,5,2), date(2026,5,1))
    assert not is_valid_leave_range(None, date(2026,5,1))


def test_is_valid_overtime_hours():
    assert is_valid_overtime_hours(1)
    assert is_valid_overtime_hours(0.25)
    assert not is_valid_overtime_hours(0)
    assert not is_valid_overtime_hours(-1)
    assert not is_valid_overtime_hours(None)


def test_is_at_least_days_ahead():
    today = date(2026, 5, 20)
    assert is_at_least_days_ahead(date(2026, 5, 21), today, 1)
    assert not is_at_least_days_ahead(date(2026, 5, 20), today, 1)
    assert is_at_least_days_ahead(date(2026, 5, 23), today)
    assert not is_at_least_days_ahead(date(2026, 5, 22), today)
    assert not is_at_least_days_ahead(None, today)


def test_ranges_overlap():
    assert ranges_overlap(date(2026,5,1), date(2026,5,3), date(2026,5,3), date(2026,5,5))
    assert ranges_overlap(date(2026,5,1), date(2026,5,3), date(2026,5,2), date(2026,5,2))
    assert not ranges_overlap(date(2026,5,1), date(2026,5,1), date(2026,5,2), date(2026,5,2))
    assert not ranges_overlap(None, date(2026,5,1), date(2026,5,1), date(2026,5,1))
