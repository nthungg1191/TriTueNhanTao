from datetime import datetime, date, time as dt_time

from app.models.attendance import Attendance


class MockSchedule:
    def __init__(self, start=dt_time(8, 0), end=dt_time(17, 0)):
        self.shift_start = start
        self.shift_end = end

    def is_effective_on(self, d: date):
        return True

    def is_weekday_allowed(self, weekday: int) -> bool:
        return True


class MockEmployee:
    def __init__(self):
        self.id = 1
        self.name = 'Test User'
        self.employee_code = 'EMPTEST'
        self._schedule = MockSchedule()

    def get_current_schedule(self):
        return self._schedule


def make_attendance(
    ci1: datetime | None,
    co1: datetime | None,
    ci2: datetime | None = None,
    co2: datetime | None = None,
):
    base_date = ci1.date() if ci1 else (co1.date() if co1 else (ci2.date() if ci2 else (co2.date() if co2 else date.today())))
    a = Attendance(employee_id=1, date=base_date)
    # Assign employee bypassing SQLAlchemy instrumentation
    a.__dict__['employee'] = MockEmployee()
    a.check_in_time = ci1
    a.check_out_time = co1
    a.check_in_time_2 = ci2
    a.check_out_time_2 = co2
    if ci1:
        a.date = ci1.date()
    a.update_status()
    return a


def test_on_time_full_day():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = make_attendance(ci1, co1, ci2, co2)
    assert a.status == 'present'
    sd = a.get_shift_breakdown()
    assert sd['morning'] == 'on_time'
    assert sd['lunch'] == 'on_time'
    assert sd['afternoon'] == 'on_time'
    assert sd['final'] == 'on_time'
    labels = a.get_shift_breakdown_labels()
    assert labels['morning'] == 'Đúng giờ'
    assert labels['lunch'] == 'Nghỉ giữa giờ đúng giờ'
    assert labels['afternoon'] == 'Vào làm đúng giờ'
    assert labels['final'] == 'Tan làm đúng giờ'
    assert a.get_status_label() == 'Đi làm đúng giờ'


def test_late_morning():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 1))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = make_attendance(ci1, co1, ci2, co2)
    assert a.status == 'late'
    assert a.get_shift_breakdown()['morning'] == 'late'


def test_lunch_early():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(11, 30))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = make_attendance(ci1, co1, ci2, co2)
    assert a.status == 'early_leave'
    sd = a.get_shift_breakdown()
    assert sd['lunch'] == 'early'


def test_lunch_boundary_is_on_time():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = make_attendance(ci1, co1, ci2, co2)
    assert a.status == 'present'
    assert a.get_shift_breakdown()['lunch'] == 'on_time'


def test_afternoon_late_before_final_checkout():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 1))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = make_attendance(ci1, co1, ci2, co2)
    assert a.status == 'late'
    assert a.get_shift_breakdown()['afternoon'] == 'late'


def test_missing_check_in():
    today = date.today()
    ci1 = None
    co1 = datetime.combine(today, dt_time(12, 0))
    a = make_attendance(ci1, co1)
    assert a.status == 'missing_check_in'


def test_missing_check_out():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = None
    a = make_attendance(ci1, co1)
    assert a.status == 'missing_check_out'


def test_missing_afternoon_check_in():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    a = make_attendance(ci1, co1)
    assert a.status == 'missing_check_in'


def test_missing_final_check_out():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = make_attendance(ci1, co1, ci2, None)
    assert a.status == 'missing_check_out'


def test_punch_sequence_supports_two_in_two_out():
    today = date.today()
    a = Attendance(employee_id=1, date=today)
    a.__dict__['employee'] = MockEmployee()

    assert a.check_in(datetime.combine(today, dt_time(8, 0))) == 1
    assert a.check_out(datetime.combine(today, dt_time(12, 0))) == 1
    assert a.check_in(datetime.combine(today, dt_time(13, 0))) == 2
    assert a.check_out(datetime.combine(today, dt_time(17, 0))) == 2

    assert a.status == 'present'
    assert a.working_hours == 8.0


def test_lunch_one_hour_early_deducts_one_day():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    # leave for lunch at 11:00 (1 hour early from 12:00)
    co1 = datetime.combine(today, dt_time(11, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = make_attendance(ci1, co1, ci2, co2)
    # Deduct should be 1 công -> working hours = 8 - 8 = 0
    a.calculate_working_hours()
    assert a.working_hours == 7.0
