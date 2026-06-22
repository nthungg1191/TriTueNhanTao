from datetime import date, timedelta

from app.models.time_off import OvertimeRequest, LeaveRequest


def test_overtime_request_status_helpers():
    req = OvertimeRequest(status='withdrawn')

    assert req.status_label == 'Đã thu hồi'
    assert req.status_badge_class == 'status-withdrawn'


def test_overtime_request_cancelled_status_helpers():
    req = OvertimeRequest(status='cancelled', date=date.today() - timedelta(days=1))

    assert req.status_label == 'Đã quá hạn'
    assert req.status_badge_class == 'status-cancelled'


def test_leave_request_status_helpers():
    req = LeaveRequest(status='pending')

    assert req.status_label == 'Chờ duyệt'
    assert req.status_badge_class == 'status-pending'


def test_leave_request_cancelled_status_helpers():
    req = LeaveRequest(status='cancelled', end_date=date.today() - timedelta(days=1))

    assert req.status_label == 'Đã quá hạn'
    assert req.status_badge_class == 'status-cancelled'