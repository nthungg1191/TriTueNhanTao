"""Attendance model"""
from app import db
from datetime import datetime, timezone, time as dt_time
from math import ceil


class Attendance(db.Model):
    """Attendance model for check-in/check-out records"""
    
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    check_in_time_2 = db.Column(db.DateTime, nullable=True)
    check_out_time_2 = db.Column(db.DateTime, nullable=True)
    overtime_check_in_time = db.Column(db.DateTime, nullable=True)
    overtime_check_out_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='present', nullable=False)  # present, absent, late, early_leave, missing_check_in, missing_check_out
    working_hours = db.Column(db.Float, default=0.0)  # Hours worked
    overtime_hours = db.Column(db.Float, default=0.0)  # Overtime hours
    notes = db.Column(db.Text, nullable=True)
    check_in_photo = db.Column(db.String(255), nullable=True)
    check_out_photo = db.Column(db.String(255), nullable=True)
    check_in_photo_2 = db.Column(db.String(255), nullable=True)
    check_out_photo_2 = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Composite index for faster queries
    __table_args__ = (
        db.Index('idx_employee_date', 'employee_id', 'date'),
    )

    STATUS_LABELS = {
        'present': 'Đi làm đúng giờ',
        'late': 'Đi làm muộn',
        'absent': 'Vắng mặt',
        'early_leave': 'Nghỉ sớm',
        'missing_check_in': 'Thiếu check-in',
        'missing_check_out': 'Thiếu check-out',
    }

    SHIFT_LABELS = {
        'morning': {
            'on_time': 'Đúng giờ',
            'late': 'Đi muộn',
            'missing': 'Thiếu check-in',
            'n/a': '--',
        },
        'lunch': {
            'on_time': 'Nghỉ giữa giờ đúng giờ',
            'early': 'Nghỉ giữa giờ sớm',
            'missing': 'Thiếu check-out',
            'n/a': '--',
        },
        'afternoon': {
            'on_time': 'Vào làm đúng giờ',
            'late': 'Vào làm muộn',
            'missing': 'Thiếu check-in',
            'n/a': '--',
        },
        'final': {
            'on_time': 'Tan làm đúng giờ',
            'early': 'Tan làm sớm',
            'missing': 'Thiếu check-out',
            'n/a': '--',
        },
    }
    
    def __repr__(self):
        return f'<Attendance {self.employee_id} on {self.date}>'
    
    def check_in(self, timestamp=None):
        """Record check-in time"""
        if timestamp is None:
            timestamp = datetime.now()
        if self.check_in_time is None:
            self.check_in_time = timestamp
            punch_slot = 1
        elif self.check_out_time is not None and self.check_in_time_2 is None:
            self.check_in_time_2 = timestamp
            punch_slot = 2
        else:
            raise ValueError('No available check-in slot for today')
        self.date = timestamp.date()
        self.update_status()
        return punch_slot
    
    def check_out(self, timestamp=None):
        """Record check-out time"""
        if timestamp is None:
            timestamp = datetime.now()
        if self.check_in_time is not None and self.check_out_time is None:
            self.check_out_time = timestamp
            punch_slot = 1
        elif self.check_in_time_2 is not None and self.check_out_time_2 is None:
            self.check_out_time_2 = timestamp
            punch_slot = 2
        else:
            raise ValueError('No available check-out slot for today')
        self.calculate_working_hours()
        self.update_status()
        return punch_slot
    
    def calculate_working_hours(self):
        """Calculate credited administrative points and overtime points.

        A complete administrative day starts from 8 points and deducts 0.5
        points per violation block. Incomplete days keep the actual hours
        earned from complete punch pairs so partial attendance does not become
        a full 8-point day.
        """
        admin_deductions = Attendance._apply_time_deductions(self)

        if self._has_complete_admin_day():
            admin_hours = max(0.0, 8.0 - admin_deductions)
        else:
            admin_hours = 0.0
            for check_in_time, check_out_time in (
                (self.check_in_time, self.check_out_time),
                (self.check_in_time_2, self.check_out_time_2),
            ):
                if check_in_time and check_out_time:
                    delta = check_out_time - check_in_time
                    admin_hours += max(delta.total_seconds(), 0) / 3600
            admin_hours = max(0.0, admin_hours - admin_deductions)

        # Cap administrative working hours to the standard 8-hour day.
        # This prevents early check-ins or late check-outs from inflating
        # the credited administrative hours beyond 8.0.
        admin_hours = min(admin_hours, 8.0)

        self.working_hours = round(admin_hours, 2)
        self.overtime_hours = round(Attendance._calculate_overtime_hours(self), 2)

    def _has_complete_admin_day(self):
        return all([
            self.check_in_time is not None,
            self.check_out_time is not None,
            self.check_in_time_2 is not None,
            self.check_out_time_2 is not None,
        ])

    def _get_violation_deduction(self, minutes):
        """Convert a violation duration into a point deduction."""
        try:
            violation_minutes = float(minutes)
        except Exception:
            return 0.0

        if violation_minutes <= 0:
            return 0.0

        return round(ceil(violation_minutes / 30.0) * 0.5, 2)

    def _calculate_deduction(self, minutes):
        """Backward-compatible helper used by older tests."""
        return self._get_violation_deduction(minutes)

    def _apply_time_deductions(self):
        """Calculate total administrative deductions for the day."""
        total_deduction = 0.0

        if self.check_in_time:
            morning_late_minutes = (self.check_in_time - datetime.combine(self.date, dt_time(8, 0))).total_seconds() / 60
            total_deduction += Attendance._get_violation_deduction(self, morning_late_minutes)

        if self.check_out_time:
            lunch_early_minutes = (datetime.combine(self.date, dt_time(12, 0)) - self.check_out_time).total_seconds() / 60
            total_deduction += Attendance._get_violation_deduction(self, lunch_early_minutes)

        if self.check_in_time_2:
            afternoon_late_minutes = (self.check_in_time_2 - datetime.combine(self.date, dt_time(13, 0))).total_seconds() / 60
            total_deduction += Attendance._get_violation_deduction(self, afternoon_late_minutes)

        if self.check_out_time_2:
            final_early_minutes = (datetime.combine(self.date, dt_time(17, 0)) - self.check_out_time_2).total_seconds() / 60
            total_deduction += Attendance._get_violation_deduction(self, final_early_minutes)

        return round(total_deduction, 2)

    def _get_approved_overtime_request(self):
        """Return an approved overtime request for this attendance date if any."""
        employee_id = self.__dict__.get('employee_id')
        attendance_date = self.__dict__.get('date')

        if not employee_id or not attendance_date:
            return None

        try:
            from app.models.time_off import OvertimeRequest
        except Exception:
            return None

        try:
            return OvertimeRequest.query.filter_by(
                employee_id=employee_id,
                date=attendance_date,
                status='approved'
            ).order_by(OvertimeRequest.created_at.desc()).first()
        except Exception:
            return None

    def _calculate_overtime_deductions(self):
        """Calculate OT deductions using the approved OT time window."""
        total_deduction = 0.0
        attendance_date = self.__dict__.get('date')
        if not attendance_date:
            return 0.0

        overtime_check_in_time = self.__dict__.get('overtime_check_in_time')
        overtime_check_out_time = self.__dict__.get('overtime_check_out_time')
        ot_start = datetime.combine(attendance_date, dt_time(17, 30))
        ot_end = datetime.combine(attendance_date, dt_time(20, 0))

        if overtime_check_in_time and overtime_check_in_time > ot_start:
            late_minutes = (overtime_check_in_time - ot_start).total_seconds() / 60
            total_deduction += Attendance._get_violation_deduction(self, late_minutes)

        if overtime_check_out_time and overtime_check_out_time < ot_end:
            early_minutes = (ot_end - overtime_check_out_time).total_seconds() / 60
            total_deduction += Attendance._get_violation_deduction(self, early_minutes)

        return round(total_deduction, 2)

    def _calculate_overtime_hours(self):
        """Calculate overtime points for an approved OT session.
        
        OT window: 17:30 - 20:00 (2.5 hours max)
        OT points = actual_hours * 1.5 (capped at 2.5 hours real time)
        Deductions applied per 30-minute late/early blocks.
        """
        request = self._get_approved_overtime_request()
        if not request:
            return 0.0

        overtime_check_in_time = self.__dict__.get('overtime_check_in_time')
        overtime_check_out_time = self.__dict__.get('overtime_check_out_time')

        if not overtime_check_in_time or not overtime_check_out_time:
            return 0.0

        delta = overtime_check_out_time - overtime_check_in_time
        actual_hours = max(delta.total_seconds(), 0) / 3600
        if actual_hours <= 0:
            return 0.0

        # Cap actual OT hours at 2.5 (OT window is 17:30-20:00)
        actual_hours = min(actual_hours, 2.5)
        
        overtime_points = actual_hours * 1.5
        overtime_points -= self._calculate_overtime_deductions()
        return max(0.0, overtime_points)
    
    def get_working_hours_display(self):
        """Format working hours for display: show minutes if < 1 hour, else show hours"""
        if not self.check_in_time and not self.check_out_time and not self.check_in_time_2 and not self.check_out_time_2:
            return '--'

        self.calculate_working_hours()
        
        seconds = max(self.working_hours * 3600, 0)
        
        if seconds < 3600:
            # Less than 1 hour: show minutes
            minutes = int(seconds / 60)
            return f"{minutes} phút"
        else:
            # 1 hour or more: show hours with 2 decimals
            hours = round(seconds / 3600, 2)
            return f"{hours}h"
    
    def update_status(self):
        """Update attendance status based on check-in/out times"""
        # Standardized rules for day shift 08:00-17:00 with lunch break 12:00-13:00.
        # Missing punches are tracked separately so they don't get mixed with
        # present/late/early_leave.

        # Missing punches handling
        if not self.check_in_time and not self.check_out_time and not self.check_in_time_2 and not self.check_out_time_2:
            self.status = 'absent'
            return

        if not self.check_in_time:
            self.status = 'missing_check_in'
            return

        if self.check_in_time and not self.check_out_time:
            self.status = 'missing_check_out'
            return

        if self.check_in_time_2 is None:
            self.status = 'missing_check_in'
            return

        if self.check_out_time_2 is None:
            self.status = 'missing_check_out'
            return

        morning_deadline = datetime.combine(self.date, dt_time(8, 0))
        lunch_boundary = datetime.combine(self.date, dt_time(12, 0))
        lunch_return = datetime.combine(self.date, dt_time(13, 0))
        final_end = datetime.combine(self.date, dt_time(17, 0))

        morning_late = self.check_in_time > morning_deadline
        lunch_early = self.check_out_time < lunch_boundary
        afternoon_late = self.check_in_time_2 > lunch_return
        final_early = self.check_out_time_2 < final_end

        # Apply status priority:
        # 1) morning/afternoon late -> 'late'
        # 2) lunch early or final early -> 'early_leave'
        # 3) otherwise -> 'present'

        if morning_late or afternoon_late:
            self.status = 'late'
            return

        if lunch_early:
            self.status = 'early_leave'
            return

        if final_early:
            self.status = 'early_leave'
            return

        self.status = 'present'
    
    def is_complete(self):
        """Check if both check-in and check-out are recorded"""
        return all([
            self.check_in_time is not None,
            self.check_out_time is not None,
            self.check_in_time_2 is not None,
            self.check_out_time_2 is not None,
        ])

    def get_status_label(self):
        """Return a human-readable label for the overall attendance status."""
        return self.STATUS_LABELS.get(self.status, self.status)

    def get_shift_breakdown_labels(self):
        """Return Vietnamese labels for each shift part."""
        breakdown = self.get_shift_breakdown()
        return {
            part: self.SHIFT_LABELS.get(part, {}).get(value, value)
            for part, value in breakdown.items()
        }

    def get_overtime_breakdown(self):
        """Return a breakdown for the OT session."""
        breakdown = {
            'approval': 'missing',
            'check_in': 'missing',
            'check_out': 'missing',
        }

        request = self._get_approved_overtime_request()
        if not request:
            return breakdown

        breakdown['approval'] = 'approved'

        overtime_check_in_time = self.__dict__.get('overtime_check_in_time')
        overtime_check_out_time = self.__dict__.get('overtime_check_out_time')

        if overtime_check_in_time:
            breakdown['check_in'] = 'on_time' if overtime_check_in_time.time() <= dt_time(17, 30) else 'late'

        if overtime_check_out_time:
            breakdown['check_out'] = 'on_time' if overtime_check_out_time.time() >= dt_time(20, 0) else 'early'

        return breakdown

    def get_shift_breakdown(self):
        """Return a breakdown of shift parts according to the standardized rules.

        Returns a dict with keys: morning, lunch, afternoon, final. Each value is one of
        'on_time', 'late', 'early', 'missing', or 'n/a'.
        """
        breakdown = {
            'morning': 'n/a',
            'lunch': 'n/a',
            'afternoon': 'n/a',
            'final': 'n/a'
        }

        if not self.check_in_time and not self.check_out_time and not self.check_in_time_2 and not self.check_out_time_2:
            breakdown['morning'] = breakdown['lunch'] = breakdown['afternoon'] = breakdown['final'] = 'missing'
            return breakdown

        if self.check_in_time is None:
            breakdown['morning'] = 'missing'
        else:
            breakdown['morning'] = 'on_time' if self.check_in_time.time() <= dt_time(8, 0) else 'late'

        if self.check_out_time is None:
            breakdown['lunch'] = 'missing'
        else:
            breakdown['lunch'] = 'early' if self.check_out_time.time() < dt_time(12, 0) else 'on_time'

        if self.check_in_time_2 is None:
            breakdown['afternoon'] = 'missing'
        else:
            breakdown['afternoon'] = 'late' if self.check_in_time_2.time() > dt_time(13, 0) else 'on_time'

        if self.check_out_time_2 is None:
            breakdown['final'] = 'missing'
        else:
            breakdown['final'] = 'on_time' if self.check_out_time_2.time() >= dt_time(17, 0) else 'early'

        return breakdown
    
    def to_dict(self):
        """Convert to dictionary"""
        # compute actual overtime raw hours if timestamps present and an approved request exists
        overtime_actual = None
        try:
            req = self._get_approved_overtime_request()
            if req and self.overtime_check_in_time and self.overtime_check_out_time:
                delta = self.overtime_check_out_time - self.overtime_check_in_time
                overtime_actual = round(max(delta.total_seconds(), 0) / 3600, 2)
        except Exception:
            overtime_actual = None

        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'employee_code': self.employee.employee_code if self.employee else None,
            'date': self.date.isoformat(),
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'check_in_time_2': self.check_in_time_2.isoformat() if self.check_in_time_2 else None,
            'check_out_time_2': self.check_out_time_2.isoformat() if self.check_out_time_2 else None,
            'overtime_check_in_time': self.overtime_check_in_time.isoformat() if self.overtime_check_in_time else None,
            'overtime_check_out_time': self.overtime_check_out_time.isoformat() if self.overtime_check_out_time else None,
            'check_in_photo': self.check_in_photo,
            'check_out_photo': self.check_out_photo,
            'check_in_photo_2': self.check_in_photo_2,
            'check_out_photo_2': self.check_out_photo_2,
            'punches': [
                {'type': 'check-in', 'slot': 1, 'time': self.check_in_time.isoformat() if self.check_in_time else None},
                {'type': 'check-out', 'slot': 1, 'time': self.check_out_time.isoformat() if self.check_out_time else None},
                {'type': 'check-in', 'slot': 2, 'time': self.check_in_time_2.isoformat() if self.check_in_time_2 else None},
                {'type': 'check-out', 'slot': 2, 'time': self.check_out_time_2.isoformat() if self.check_out_time_2 else None},
            ],
            'status': self.status,
            'status_label': self.get_status_label(),
            'working_hours': self.working_hours,
            'working_hours_display': self.get_working_hours_display(),
            # 'overtime_hours' is stored as OT points (1.5x raw hours minus deductions)
            'overtime_hours': self.overtime_hours,
            'overtime_actual_hours': overtime_actual,
            'notes': self.notes,
            'is_complete': self.is_complete(),
            'shift_breakdown': self.get_shift_breakdown(),
            'shift_breakdown_labels': self.get_shift_breakdown_labels(),
            'overtime_breakdown': self.get_overtime_breakdown(),
        }

