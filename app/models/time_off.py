"""Models for employee overtime and leave requests"""
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
    def is_overdue(self):
        return self.status == 'pending' and self.date is not None and self.date < date.today()

    @property
    def status_label(self):
        if self.is_overdue:
            return 'Yêu cầu quá hạn'

        labels = {
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'rejected': 'Từ chối',
            'withdrawn': 'Đã thu hồi',
        }
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self):
        if self.is_overdue:
            return 'status-overdue'

        classes = {
            'pending': 'status-pending',
            'approved': 'status-approved',
            'rejected': 'status-rejected',
            'withdrawn': 'status-withdrawn',
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
    def is_overdue(self):
        return self.status == 'pending' and self.end_date is not None and self.end_date < date.today()

    @property
    def status_label(self):
        if self.is_overdue:
            return 'Yêu cầu quá hạn'

        labels = {
            'pending': 'Chờ duyệt',
            'approved': 'Đã duyệt',
            'rejected': 'Từ chối',
            'withdrawn': 'Đã thu hồi',
        }
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self):
        if self.is_overdue:
            return 'status-overdue'

        classes = {
            'pending': 'status-pending',
            'approved': 'status-approved',
            'rejected': 'status-rejected',
            'withdrawn': 'status-withdrawn',
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
