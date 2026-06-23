"""Automated scheduler to cancel overdue pending requests."""
import logging
from datetime import date

logger = logging.getLogger(__name__)


def cancel_overdue_requests(app):
    """Find pending requests past their deadline and set status to 'cancelled'."""
    with app.app_context():
        from app import db
        from app.models.time_off import (
            OvertimeRequest, LeaveRequest, AttendanceCorrectionRequest,
        )

        today = date.today()
        total = 0

        # Overtime: pending and date < today
        ot_q = OvertimeRequest.query.filter(
            OvertimeRequest.status == 'pending',
            OvertimeRequest.date < today,
        )
        for r in ot_q.all():
            r.status = 'cancelled'
            total += 1

        # Leave: pending and end_date < today
        leave_q = LeaveRequest.query.filter(
            LeaveRequest.status == 'pending',
            LeaveRequest.end_date < today,
        )
        for r in leave_q.all():
            r.status = 'cancelled'
            total += 1

        if total:
            db.session.commit()
            logger.info('Auto-cancelled %d overdue request(s)', total)