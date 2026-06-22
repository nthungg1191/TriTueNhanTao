"""Models for employee overtime, leave requests and attendance corrections"""
from app import db
from datetime import datetime, date


class OvertimeRequest(db.Model):
    __tablename__ = 'overtime_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, default=0.0, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # Review metadata
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    admin_note = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', backref='overtime_requests', lazy='joined')

    def __repr__(self):
        return f'<Overtime {self.employee_id} {self.date} {self.hours}h>'

    @property
    def status_label(self):
        labels = {
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'rejected': 'Từ chối',
            'withdrawn': 'Đã thu hồi',
            'cancelled': 'Đã quá hạn',
        }
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self):
        classes = {
            'pending': 'status-pending',
            'approved': 'status-approved',
            'rejected': 'status-rejected',
            'withdrawn': 'status-withdrawn',
            'cancelled': 'status-cancelled',
        }
        return classes.get(self.status, 'status-secondary')

    @property
    def kind_label(self):
        if self.date and self.date.weekday() == 6 and self.hours >= 7.5:
            return 'Làm Chủ nhật'
        return 'Tăng ca 17:30-20:00'

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date.isoformat() if isinstance(self.date, date) else self.date,
            'hours': self.hours,
            'reason': self.reason,
            'status': self.status,
            'status_label': self.status_label,
            'kind_label': self.kind_label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # Review metadata
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    admin_note = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', backref='leave_requests', lazy='joined')

    def __repr__(self):
        return f'<Leave {self.employee_id} {self.start_date} - {self.end_date}>'

    @property
    def status_label(self):
        labels = {
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'rejected': 'Từ chối',
            'withdrawn': 'Đã thu hồi',
            'cancelled': 'Đã quá hạn',
        }
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self):
        classes = {
            'pending': 'status-pending',
            'approved': 'status-approved',
            'rejected': 'status-rejected',
            'withdrawn': 'status-withdrawn',
            'cancelled': 'status-cancelled',
        }
        return classes.get(self.status, 'status-secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date,
            'reason': self.reason,
            'status': self.status,
            'status_label': self.status_label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AttendanceCorrectionRequest(db.Model):
    """Yêu cầu bổ sung/chỉnh sửa chấm công từ nhân viên"""
    __tablename__ = 'attendance_correction_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)

    reason_type = db.Column(db.String(30), nullable=False)  # missing_check_in / missing_check_out / wrong_time / absent_correction / other

    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    check_in_time_2 = db.Column(db.DateTime, nullable=True)
    check_out_time_2 = db.Column(db.DateTime, nullable=True)

    explanation = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/approved/rejected/withdrawn
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    admin_note = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', backref='correction_requests', lazy='joined')

    REASON_TYPE_LABELS = {
        'missing_check_in': 'Thiếu check-in',
        'missing_check_out': 'Thiếu check-out',
        'wrong_time': 'Sai giờ',
        'absent_correction': 'Bổ sung vắng mặt',
        'other': 'Lý do khác',
    }

    __table_args__ = (
        db.Index('idx_correction_employee_date', 'employee_id', 'date'),
    )

    def __repr__(self):
        return f'<AttendanceCorrection {self.employee_id} {self.date} [{self.reason_type}]>'

    @property
    def status_label(self):
        labels = {
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'rejected': 'Từ chối',
            'withdrawn': 'Đã thu hồi',
        }
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self):
        classes = {
            'pending': 'status-pending',
            'approved': 'status-approved',
            'rejected': 'status-rejected',
            'withdrawn': 'status-withdrawn',
        }
        return classes.get(self.status, 'status-secondary')

    @property
    def reason_type_label(self):
        return self.REASON_TYPE_LABELS.get(self.reason_type, self.reason_type)

    def to_dict(self):
        from app.utils.timezone_utils import format_time_24h
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'employee_code': self.employee.employee_code if self.employee else None,
            'date': self.date.isoformat() if isinstance(self.date, date) else self.date,
            'reason_type': self.reason_type,
            'reason_type_label': self.reason_type_label,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'check_in_time_2': self.check_in_time_2.isoformat() if self.check_in_time_2 else None,
            'check_out_time_2': self.check_out_time_2.isoformat() if self.check_out_time_2 else None,
            'check_in_time_local': format_time_24h(self.check_in_time),
            'check_out_time_local': format_time_24h(self.check_out_time),
            'check_in_time_2_local': format_time_24h(self.check_in_time_2),
            'check_out_time_2_local': format_time_24h(self.check_out_time_2),
            'explanation': self.explanation,
            'status': self.status,
            'status_label': self.status_label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
