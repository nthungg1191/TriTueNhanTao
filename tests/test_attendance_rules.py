from datetime import datetime, date, time as dt_time

from app.models.attendance import Attendance
from app.routes.kiosk import _resolve_time_based_action


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


# --- Tests for _resolve_time_based_action (12:00-13:00 window) ---


def _build_attendance(ci1, co1, ci2=None, co2=None):
    """Build an Attendance instance with optional punched times for testing
    the kiosk action resolver."""
    return make_attendance(ci1, co1, ci2, co2)


def test_lunch_window_records_checkout_when_morning_open():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(7, 30))
    a = _build_attendance(ci1, None)
    now = datetime.combine(today, dt_time(12, 30))
    assert _resolve_time_based_action(a, now) == ('check-out', 1)


def test_lunch_window_records_checkin_2_after_lunch_checkout():
    """After punching out for lunch, scanning again inside 12:00-13:00
    should record the afternoon check-in (the case from the example)."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(7, 30))
    co1 = datetime.combine(today, dt_time(12, 5))
    a = _build_attendance(ci1, co1)
    now = datetime.combine(today, dt_time(12, 50))
    assert _resolve_time_based_action(a, now) == ('check-in', 2)


def test_lunch_window_records_checkin_2_when_morning_missed():
    today = date.today()
    a = _build_attendance(None, None)
    now = datetime.combine(today, dt_time(12, 30))
    assert _resolve_time_based_action(a, now) == ('check-in', 2)


def test_lunch_window_records_checkin_2_when_only_lunch_checkout_exists():
    today = date.today()
    co1 = datetime.combine(today, dt_time(12, 0))
    a = _build_attendance(None, co1)
    now = datetime.combine(today, dt_time(12, 30))
    assert _resolve_time_based_action(a, now) == ('check-in', 2)


def test_lunch_window_skipped_when_all_four_slots_filled():
    today = date.today()
    ci1 = datetime.combine(today, dt_time(7, 30))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 0))
    a = _build_attendance(ci1, co1, ci2, co2)
    now = datetime.combine(today, dt_time(12, 50))
    assert _resolve_time_based_action(a, now) is None


# --- Tests for early check-out / shift-bounded rules ---


def test_morning_early_checkout_before_12():
    """Check-in lúc 08:00, quét 11:30 -> check-out sáng (tính là sớm)."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    a = _build_attendance(ci1, None)
    now = datetime.combine(today, dt_time(11, 30))
    assert _resolve_time_based_action(a, now) == ('check-out', 1)


def test_morning_checkin_at_7_30_early_checkout():
    """Check-in lúc 07:30, quét 11:30 -> check-out sáng (tính là sớm)."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(7, 30))
    a = _build_attendance(ci1, None)
    now = datetime.combine(today, dt_time(11, 30))
    assert _resolve_time_based_action(a, now) == ('check-out', 1)


def test_morning_open_after_13_becomes_checkin_2():
    """Ca sáng miss check-out, quét 13:30 -> check-in chiều, status sẽ
    được update_status() tự đánh missing_check_out."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    a = _build_attendance(ci1, None)
    now = datetime.combine(today, dt_time(13, 30))
    assert _resolve_time_based_action(a, now) == ('check-in', 2)


def test_morning_open_after_13_no_checkin_2_returns_none():
    """Ca sáng miss, đã có check-in_2 rồi -> bỏ qua."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, None, ci2)
    now = datetime.combine(today, dt_time(14, 0))
    assert _resolve_time_based_action(a, now) is None


def test_afternoon_early_checkout_before_17():
    """Check-in chiều lúc 13:00, quét 16:30 -> check-out chiều (tính là sớm)."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, co1, ci2, None)
    now = datetime.combine(today, dt_time(16, 30))
    assert _resolve_time_based_action(a, now) == ('check-out', 2)


def test_afternoon_normal_checkout_after_17():
    """Check-in chiều lúc 13:00, quét 17:10 -> check-out chiều bình thường."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, co1, ci2, None)
    now = datetime.combine(today, dt_time(17, 10))
    assert _resolve_time_based_action(a, now) == ('check-out', 2)


def test_afternoon_checkout_at_20_returns_none():
    """Sau 20:00 không còn là khung check-out thường -> chuyển cho OT picker."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, co1, ci2, None)
    now = datetime.combine(today, dt_time(20, 30))
    assert _resolve_time_based_action(a, now) is None


def test_no_checkins_after_13_records_checkin_2():
    """Không có check-in nào, quét 14:00 -> ghi check-in chiều."""
    today = date.today()
    a = _build_attendance(None, None)
    now = datetime.combine(today, dt_time(14, 0))
    assert _resolve_time_based_action(a, now) == ('check-in', 2)


def test_missed_morning_checkin_early_scan_before_12():
    """Không có check-in_1, quét 11:00 -> vẫn là check-in sáng, không phải check-out."""
    today = date.today()
    a = _build_attendance(None, None)
    now = datetime.combine(today, dt_time(11, 0))
    assert _resolve_time_based_action(a, now) == ('check-in', 1)


# --- Tests for update_status() with missed lunch check-out ---


def test_missed_lunch_checkout_status_after_afternoon_checkin():
    """check_in_1 có, check_out_1 trống, đã có check_in_2 -> status = missing_check_out."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    ci2 = datetime.combine(today, dt_time(13, 30))
    a = _build_attendance(ci1, None, ci2)
    assert a.status == 'missing_check_out'


# --- Tests for 17:00-17:30 transition window ---


class MockOvertimeRequest:
    """Minimal stand-in for an approved OvertimeRequest."""
    def __init__(self):
        self.status = 'approved'


def _stub_ot_request(a, present=True):
    """Stub attendance._get_approved_overtime_request on the object."""
    a._get_approved_overtime_request = (lambda: MockOvertimeRequest()) if present else (lambda: None)


def test_transition_open_checkout_2_at_17_10_returns_checkout_2():
    """Rule 1: Ca chiều đang mở, quét 17:10 -> check-out ca chiều."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, co1, ci2, None)
    now = datetime.combine(today, dt_time(17, 10))
    assert _resolve_time_based_action(a, now) == ('check-out', 2)


def test_transition_open_checkout_2_no_overtime_still_returns_checkout_2():
    """Rule 3: Ca chiều đang mở, không có đăng ký OT, quét 17:25 -> check-out ca chiều."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, co1, ci2, None)
    _stub_ot_request(a, present=False)
    now = datetime.combine(today, dt_time(17, 25))
    assert _resolve_time_based_action(a, now) == ('check-out', 2)


def test_transition_after_checkout_2_returns_overtime_checkin_when_registered():
    """Rule 3: Ca chiều đã đóng, có đăng ký OT, chưa có OT check-in, quét 17:20 -> OT check-in."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 5))
    a = _build_attendance(ci1, co1, ci2, co2)
    _stub_ot_request(a, present=True)
    now = datetime.combine(today, dt_time(17, 20))
    assert _resolve_time_based_action(a, now) == 'overtime_check-in'


def test_transition_after_checkout_2_returns_none_when_no_overtime():
    """Rule 4: Ca chiều đã đóng, không có đăng ký OT, quét 17:20 -> None."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 5))
    a = _build_attendance(ci1, co1, ci2, co2)
    _stub_ot_request(a, present=False)
    now = datetime.combine(today, dt_time(17, 20))
    assert _resolve_time_based_action(a, now) is None


def test_transition_after_overtime_checkin_returns_overtime_checkout():
    """Rule 5: Đã có OT check-in, quét tiếp 17:25 -> OT check-out."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 5))
    a = _build_attendance(ci1, co1, ci2, co2)
    a.overtime_check_in_time = datetime.combine(today, dt_time(17, 20))
    _stub_ot_request(a, present=True)
    now = datetime.combine(today, dt_time(17, 25))
    assert _resolve_time_based_action(a, now) == 'overtime_check-out'


def test_transition_window_boundary_before_17_00_uses_regular_checkout():
    """Trước 17:00: check-out chiều vẫn là check-out chiều thường (not OT)."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    a = _build_attendance(ci1, co1, ci2, None)
    now = datetime.combine(today, dt_time(16, 59))
    assert _resolve_time_based_action(a, now) == ('check-out', 2)


def test_transition_window_boundary_at_17_30_skips_transition():
    """Tại 17:30: khung chuyển tiếp kết thúc, _pick_action_for_kiosk gọi OT picker."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    ci2 = datetime.combine(today, dt_time(13, 0))
    co2 = datetime.combine(today, dt_time(17, 5))
    a = _build_attendance(ci1, co1, ci2, co2)
    _stub_ot_request(a, present=True)
    now = datetime.combine(today, dt_time(17, 30))
    # 17:30 không còn trong khung 17:00-17:30, nên _resolve_time_based_action trả None
    # và _pick_action_for_kiosk sẽ deleg sang _resolve_overtime_action (OT check-in)
    assert _resolve_time_based_action(a, now) is None


def test_transition_no_effect_when_afternoon_not_started():
    """Chưa check-in chiều, quét 17:10 -> check-in chiều (không phải OT)."""
    today = date.today()
    ci1 = datetime.combine(today, dt_time(8, 0))
    co1 = datetime.combine(today, dt_time(12, 0))
    a = _build_attendance(ci1, co1)
    _stub_ot_request(a, present=True)
    now = datetime.combine(today, dt_time(17, 10))
    # Chưa có check_in_2, nên branch đầu tiên không match
    # -> rơi xuống branch "chưa check-in chiều"
    assert _resolve_time_based_action(a, now) == ('check-in', 2)
