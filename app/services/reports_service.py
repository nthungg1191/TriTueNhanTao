"""Reports Service - Xử lý logic báo cáo và thống kê"""
from app import db
from app.models import Employee, Attendance, Department, WorkSchedule
from datetime import date, datetime, timedelta, time as dt_time
from sqlalchemy import func, and_, or_, extract
from collections import defaultdict
import calendar


_STATUS_LABELS = {
    'present': 'Có mặt',
    'absent': 'Vắng mặt',
    'early_leave': 'Rời sớm',
    'late': 'Đi muộn',
}


def _status_label(s):
    """Trả về nhãn tiếng Việt ngắn gọn cho mã trạng thái."""
    return _STATUS_LABELS.get(s, s)


def _query_attendances_in_range(start_dt, end_dt):
    """Lấy attendance theo khoảng [start_dt, end_dt).

    Bản ghi được tính khi:
    - ``check_in_time`` (DateTime) thuộc khoảng, HOẶC
    - ``date`` (Date) nằm trong khoảng ngày tương ứng.
    Việc kết hợp cả hai tránh sai lệch khi dữ liệu cũ dùng ``date``
    nhưng check-in lại ở ngày khác (hoặc ngược lại).
    """
    return Attendance.query.filter(
        or_(
            and_(Attendance.check_in_time >= start_dt, Attendance.check_in_time < end_dt),
            and_(Attendance.date >= start_dt.date(), Attendance.date < end_dt.date())
        )
    ).all()


def _resolve_status(att):
    """Tính trạng thái từ dữ liệu chấm công thực tế.

    Không phụ thuộc cột ``status`` đã lưu trong DB (vốn có thể lệch với dữ
    liệu punch thực tế nếu bản ghi được tạo trước/sau khi cập nhật logic).

    Returns
    -------
    dict
        ``main``: ``'present' | 'absent' | 'early_leave'``
        ``late_minutes``: tổng phút đi muộn (sáng + chiều)
        ``has_any_punch``: True nếu có ít nhất một mốc chấm công
    """
    has_morning_in = att.check_in_time is not None
    has_morning_out = att.check_out_time is not None
    has_afternoon_in = att.check_in_time_2 is not None
    has_afternoon_out = att.check_out_time_2 is not None
    has_any_punch = has_morning_in or has_morning_out or has_afternoon_in or has_afternoon_out

    if not has_any_punch:
        return {'main': 'absent', 'late_minutes': 0, 'has_any_punch': False}

    late_minutes = 0
    attendance_date = att.date
    if attendance_date is None and has_morning_in:
        attendance_date = att.check_in_time.date()

    if attendance_date is not None:
        if has_morning_in:
            morning_deadline = datetime.combine(attendance_date, dt_time(8, 0))
            if att.check_in_time > morning_deadline:
                late_minutes += int((att.check_in_time - morning_deadline).total_seconds() // 60)
        if has_afternoon_in:
            afternoon_deadline = datetime.combine(attendance_date, dt_time(13, 0))
            if att.check_in_time_2 > afternoon_deadline:
                late_minutes += int((att.check_in_time_2 - afternoon_deadline).total_seconds() // 60)

    early = False
    if attendance_date is not None and has_morning_out and has_afternoon_out:
        lunch_end = datetime.combine(attendance_date, dt_time(12, 0))
        final_end = datetime.combine(attendance_date, dt_time(17, 0))
        if att.check_out_time < lunch_end or att.check_out_time_2 < final_end:
            early = True

    return {
        'main': 'early_leave' if early else 'present',
        'late_minutes': late_minutes,
        'has_any_punch': True,
    }


class ReportsService:
    """Service for generating attendance reports and statistics"""
    
    @staticmethod
    def get_daily_report(report_date: date = None):
        """Báo cáo theo ngày.

        Liệt kê TẤT CẢ nhân viên active và tính trạng thái dựa trên dữ liệu
        chấm công thực tế (sự tồn tại của ``check_in_time``/``check_out_time``),
        không phụ thuộc cột ``status`` đã lưu trong DB.
        """
        if report_date is None:
            report_date = date.today()

        # Tổng số nhân viên active (tính cả những người vắng mặt thực sự)
        employees = Employee.query.filter_by(is_active=True).all()
        total_employees = len(employees)

        # Khoảng thời gian [date 00:00, date+1 00:00) tránh sai lệch date/datetime
        start_dt = datetime.combine(report_date, dt_time(0, 0))
        end_dt = datetime.combine(report_date + timedelta(days=1), dt_time(0, 0))

        raw_attendances = _query_attendances_in_range(start_dt, end_dt)

        # Gom theo employee_id; ưu tiên bản ghi có check_in_time sớm nhất trong ngày
        by_employee = {}
        for a in raw_attendances:
            existing = by_employee.get(a.employee_id)
            if existing is None:
                by_employee[a.employee_id] = a
            else:
                a_in = a.check_in_time or datetime.max
                e_in = existing.check_in_time or datetime.max
                if a_in < e_in:
                    by_employee[a.employee_id] = a

        employee_statuses = []
        present_count = late_count = early_leave_count = absent_count = 0
        total_working_hours = 0.0
        attendances_for_export = []

        for emp in employees:
            att = by_employee.get(emp.id)
            if att is None:
                employee_statuses.append({
                    'employee_id': emp.id,
                    'employee_name': emp.name,
                    'employee_code': emp.employee_code,
                    'date': report_date.isoformat(),
                    'has_any_punch': False,
                    'status': 'absent',
                    'status_label': _status_label('absent'),
                    'is_late_minutes': 0,
                    'is_late': False,
                    'working_hours': 0,
                    'check_in_time': None,
                    'check_out_time': None,
                    'check_in_time_2': None,
                    'check_out_time_2': None,
                })
                absent_count += 1
                continue

            resolved = _resolve_status(att)
            att_dict = att.to_dict()
            employee_statuses.append({
                'employee_id': emp.id,
                'employee_name': emp.name,
                'employee_code': emp.employee_code,
                'date': report_date.isoformat(),
                'has_any_punch': resolved['has_any_punch'],
                'status': resolved['main'],
                'status_label': _status_label(resolved['main']),
                'is_late_minutes': resolved['late_minutes'],
                'is_late': resolved['late_minutes'] > 0,
                'working_hours': att.working_hours or 0,
                'check_in_time': att_dict.get('check_in_time'),
                'check_out_time': att_dict.get('check_out_time'),
                'check_in_time_2': att_dict.get('check_in_time_2'),
                'check_out_time_2': att_dict.get('check_out_time_2'),
            })
            attendances_for_export.append(att_dict)

            if resolved['main'] == 'absent':
                absent_count += 1
            else:
                present_count += 1
                if resolved['main'] == 'early_leave':
                    early_leave_count += 1
                if resolved['late_minutes'] > 0:
                    late_count += 1
            if att.working_hours:
                total_working_hours += att.working_hours

        on_time_count = present_count - late_count
        attendance_rate = (present_count / total_employees * 100) if total_employees > 0 else 0
        on_time_rate = (on_time_count / total_employees * 100) if total_employees > 0 else 0

        # Tổng giờ tăng ca thực tế (dựa trên overtime_check_in/out nếu có)
        total_overtime_actual_hours = 0.0
        for a in raw_attendances:
            try:
                if a.overtime_check_in_time and a.overtime_check_out_time:
                    delta = a.overtime_check_out_time - a.overtime_check_in_time
                    total_overtime_actual_hours += max(delta.total_seconds(), 0) / 3600
            except Exception:
                pass

        return {
            'date': report_date.isoformat(),
            'total_employees': total_employees,
            'checked_in': total_employees - absent_count,
            'present': present_count,
            'late': late_count,
            'absent': absent_count,
            'early_leave': early_leave_count,
            'attendance_rate': round(attendance_rate, 2),
            'on_time_rate': round(on_time_rate, 2),
            'total_working_hours': round(total_working_hours, 2),
            'total_overtime_hours': round(sum(a.overtime_hours for a in raw_attendances if a.overtime_hours), 2),
            'total_overtime_actual_hours': round(total_overtime_actual_hours, 2),
            'employee_statuses': employee_statuses,
            # Giữ key 'attendances' để tương thích export_service
            'attendances': attendances_for_export,
        }
    
    @staticmethod
    def get_weekly_report(start_date: date = None):
        """Báo cáo theo tuần"""
        if start_date is None:
            # Bắt đầu từ thứ 2 của tuần hiện tại
            today = date.today()
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)

        end_date = start_date + timedelta(days=6)

        # Lấy attendance theo khoảng datetime tránh sai lệch date/datetime
        start_dt = datetime.combine(start_date, dt_time(0, 0))
        end_dt = datetime.combine(end_date + timedelta(days=1), dt_time(0, 0))
        attendances = _query_attendances_in_range(start_dt, end_dt)

        total_employees = Employee.query.filter_by(is_active=True).count()

        # Group by date dựa trên dữ liệu chấm công thực tế
        daily_stats = {}
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            # Lấy bản ghi có check_in_time hoặc date trùng current_date
            day_attendances = [
                a for a in attendances
                if (a.date == current_date)
                or (a.check_in_time and a.check_in_time.date() == current_date)
            ]

            # Gom theo employee_id, ưu tiên check_in_time sớm nhất
            by_employee = {}
            for a in day_attendances:
                existing = by_employee.get(a.employee_id)
                if existing is None:
                    by_employee[a.employee_id] = a
                else:
                    a_in = a.check_in_time or datetime.max
                    e_in = existing.check_in_time or datetime.max
                    if a_in < e_in:
                        by_employee[a.employee_id] = a

            day_present = 0
            day_late = 0
            day_early_leave = 0
            day_working = 0.0
            for a in by_employee.values():
                resolved = _resolve_status(a)
                if resolved['main'] == 'absent':
                    continue
                day_present += 1
                if resolved['main'] == 'early_leave':
                    day_early_leave += 1
                if resolved['late_minutes'] > 0:
                    day_late += 1
                if a.working_hours:
                    day_working += a.working_hours

            daily_stats[current_date] = {
                'date': current_date.isoformat(),
                'present': day_present,
                'late': day_late,
                'absent': total_employees - day_present,
                'early_leave': day_early_leave,
                'total': day_present,
                'working_hours': round(day_working, 2)
            }

        week_total_present = sum(s['present'] for s in daily_stats.values())
        week_total_late = sum(s['late'] for s in daily_stats.values())
        week_total_absent = sum(s['absent'] for s in daily_stats.values())
        week_total_early_leave = sum(s['early_leave'] for s in daily_stats.values())
        week_total_hours = sum(s['working_hours'] for s in daily_stats.values())

        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_employees': total_employees,
            'week_total_present': week_total_present,
            'week_total_late': week_total_late,
            'week_total_absent': week_total_absent,
            'week_total_early_leave': week_total_early_leave,
            'week_total_hours': round(week_total_hours, 2),
            'average_attendance_rate': round((week_total_present / (total_employees * 7) * 100) if total_employees > 0 else 0, 2),
            'daily_stats': list(daily_stats.values())
        }
    
    @staticmethod
    def get_monthly_report(year: int = None, month: int = None):
        """Báo cáo theo tháng"""
        if year is None or month is None:
            today = date.today()
            year = today.year
            month = today.month

        start_date = date(year, month, 1)
        # Ngày cuối cùng của tháng
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        # Lấy attendance theo khoảng datetime tránh sai lệch date/datetime
        start_dt = datetime.combine(start_date, dt_time(0, 0))
        end_dt = datetime.combine(end_date + timedelta(days=1), dt_time(0, 0))
        attendances = _query_attendances_in_range(start_dt, end_dt)

        total_employees = Employee.query.filter_by(is_active=True).count()
        total_days = (end_date - start_date).days + 1

        # Thống kê tổng hợp dựa trên _resolve_status
        total_present = 0
        total_late = 0
        total_early_leave = 0
        total_working_hours = 0.0
        total_overtime_hours = 0.0
        # Tính theo từng bản ghi (đã gom theo employee_id+date qua daily_stats bên dưới)
        # Ở đây dùng cách đơn giản: _resolve_status cho từng bản ghi có punch,
        # nhưng bản ghi cùng (employee,date) đã được filter trong daily_stats.
        for a in attendances:
            resolved = _resolve_status(a)
            if resolved['main'] == 'absent':
                continue
            total_present += 1
            if resolved['main'] == 'early_leave':
                total_early_leave += 1
            if resolved['late_minutes'] > 0:
                total_late += 1
            if a.working_hours:
                total_working_hours += a.working_hours
            if a.overtime_hours:
                total_overtime_hours += a.overtime_hours

        # Tính số ngày vắng mặt: tổng ngày -m kỳ vọng - đã chấm (mỗi ngày đếm tối đa 1 lần/người)
        # daily_stats dưới đây sẽ cho biết số người có mặt từng ngày, dùng nó để tính absent.
        daily_stats = {}
        for day_offset in range(total_days):
            current_date = start_date + timedelta(days=day_offset)
            day_attendances = [
                a for a in attendances
                if (a.date == current_date)
                or (a.check_in_time and a.check_in_time.date() == current_date)
            ]
            # Gom theo employee_id, ưu tiên check_in_time sớm nhất
            by_employee = {}
            for a in day_attendances:
                existing = by_employee.get(a.employee_id)
                if existing is None:
                    by_employee[a.employee_id] = a
                else:
                    a_in = a.check_in_time or datetime.max
                    e_in = existing.check_in_time or datetime.max
                    if a_in < e_in:
                        by_employee[a.employee_id] = a

            day_present = 0
            day_late = 0
            day_early_leave = 0
            for a in by_employee.values():
                resolved = _resolve_status(a)
                if resolved['main'] == 'absent':
                    continue
                day_present += 1
                if resolved['main'] == 'early_leave':
                    day_early_leave += 1
                if resolved['late_minutes'] > 0:
                    day_late += 1

            daily_stats[current_date] = {
                'date': current_date.isoformat(),
                'present': day_present,
                'late': day_late,
                'absent': total_employees - day_present,
                'early_leave': day_early_leave,
                'total': day_present,
            }

        # Tổng hợp từ daily_stats (đảm bảo mỗi người/ngày chỉ đếm 1 lần)
        total_present = sum(s['present'] for s in daily_stats.values())
        total_late = sum(s['late'] for s in daily_stats.values())
        total_early_leave = sum(s['early_leave'] for s in daily_stats.values())
        total_absent = sum(s['absent'] for s in daily_stats.values())
        expected_attendance = total_employees * total_days

        return {
            'year': year,
            'month': month,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_employees': total_employees,
            'total_days': total_days,
            'total_present': total_present,
            'total_late': total_late,
            'total_absent': total_absent,
            'total_early_leave': total_early_leave,
            'total_working_hours': round(total_working_hours, 2),
            'total_overtime_hours': round(total_overtime_hours, 2),
            'average_attendance_rate': round((total_present / expected_attendance * 100) if expected_attendance > 0 else 0, 2),
            'on_time_rate': round(((total_present - total_late) / expected_attendance * 100) if expected_attendance > 0 else 0, 2),
            'daily_stats': list(daily_stats.values())
        }
    
    @staticmethod
    def get_department_report(report_date: date = None, department_id: int = None):
        """Báo cáo theo phòng ban"""
        if report_date is None:
            report_date = date.today()

        # Query employees
        query = Employee.query.filter_by(is_active=True)
        if department_id:
            query = query.filter_by(department_id=department_id)

        employees = query.all()
        employee_ids = [e.id for e in employees]

        # Lấy attendance theo khoảng datetime tránh sai lệch date/datetime
        start_dt = datetime.combine(report_date, dt_time(0, 0))
        end_dt = datetime.combine(report_date + timedelta(days=1), dt_time(0, 0))
        raw_attendances = _query_attendances_in_range(start_dt, end_dt)
        attendances = [a for a in raw_attendances if a.employee_id in employee_ids]

        # Gom theo employee_id
        by_employee = {}
        for a in attendances:
            existing = by_employee.get(a.employee_id)
            if existing is None:
                by_employee[a.employee_id] = a
            else:
                a_in = a.check_in_time or datetime.max
                e_in = existing.check_in_time or datetime.max
                if a_in < e_in:
                    by_employee[a.employee_id] = a

        present_count = 0
        late_count = 0
        for a in by_employee.values():
            resolved = _resolve_status(a)
            if resolved['main'] == 'absent':
                continue
            present_count += 1
            if resolved['late_minutes'] > 0:
                late_count += 1
        absent_count = len(employees) - present_count

        return {
            'date': report_date.isoformat(),
            'department_id': department_id,
            'total_employees': len(employees),
            'present': present_count,
            'late': late_count,
            'absent': absent_count,
            'attendance_rate': round((present_count / len(employees) * 100) if len(employees) > 0 else 0, 2)
        }
    
    @staticmethod
    def get_employee_attendance_summary(employee_id: int, start_date: date, end_date: date):
        """Tóm tắt chấm công của một nhân viên trong khoảng thời gian"""
        start_dt = datetime.combine(start_date, dt_time(0, 0))
        end_dt = datetime.combine(end_date + timedelta(days=1), dt_time(0, 0))
        raw = _query_attendances_in_range(start_dt, end_dt)
        attendances = [a for a in raw if a.employee_id == employee_id]

        total_days = (end_date - start_date).days + 1
        present_days = 0
        absent_days = 0
        late_days = 0
        early_leave_days = 0
        total_working_hours = 0.0

        # Gom theo (employee_id, date) - ở đây đã filter employee_id rồi
        by_date = {}
        for a in attendances:
            d = a.date or (a.check_in_time.date() if a.check_in_time else None)
            if d is None:
                continue
            existing = by_date.get(d)
            if existing is None:
                by_date[d] = a
            else:
                a_in = a.check_in_time or datetime.max
                e_in = existing.check_in_time or datetime.max
                if a_in < e_in:
                    by_date[d] = a

        for d, a in by_date.items():
            resolved = _resolve_status(a)
            if resolved['main'] == 'absent':
                absent_days += 1
                continue
            present_days += 1
            if resolved['main'] == 'early_leave':
                early_leave_days += 1
            if resolved['late_minutes'] > 0:
                late_days += 1
            if a.working_hours:
                total_working_hours += a.working_hours
        # Ngày còn lại (không có bản ghi nào) coi là vắng
        absent_days += max(0, total_days - len(by_date))

        return {
            'employee_id': employee_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'early_leave_days': early_leave_days,
            'attendance_rate': round((present_days / total_days * 100) if total_days > 0 else 0, 2),
            'total_working_hours': round(total_working_hours, 2),
            'average_hours_per_day': round(total_working_hours / present_days, 2) if present_days > 0 else 0
        }

    @staticmethod
    def get_late_employees(report_date: date = None, limit: int = 10):
        """Danh sách nhân viên đi muộn"""
        if report_date is None:
            report_date = date.today()

        # Lọc attendance trong khoảng datetime của ngày
        start_dt = datetime.combine(report_date, dt_time(0, 0))
        end_dt = datetime.combine(report_date + timedelta(days=1), dt_time(0, 0))
        raw = _query_attendances_in_range(start_dt, end_dt)

        # Gom theo employee_id, ưu tiên check_in_time sớm nhất
        by_employee = {}
        for a in raw:
            existing = by_employee.get(a.employee_id)
            if existing is None:
                by_employee[a.employee_id] = a
            else:
                a_in = a.check_in_time or datetime.max
                e_in = existing.check_in_time or datetime.max
                if a_in < e_in:
                    by_employee[a.employee_id] = a

        # Lọc các bản ghi có late_minutes > 0
        late_attendances = []
        for a in by_employee.values():
            resolved = _resolve_status(a)
            if resolved['late_minutes'] > 0:
                late_attendances.append(a)

        # Sắp xếp theo check_in_time tăng dần
        late_attendances.sort(key=lambda a: a.check_in_time or datetime.max)
        return [a.to_dict() for a in late_attendances[:limit]]

    @staticmethod
    def get_absent_employees(report_date: date = None):
        """Danh sách nhân viên vắng mặt"""
        if report_date is None:
            report_date = date.today()

        # Lấy tất cả nhân viên active
        all_employees = Employee.query.filter_by(is_active=True).all()

        # Lấy những người có bất kỳ mốc chấm công nào trong ngày
        start_dt = datetime.combine(report_date, dt_time(0, 0))
        end_dt = datetime.combine(report_date + timedelta(days=1), dt_time(0, 0))
        raw = _query_attendances_in_range(start_dt, end_dt)

        punched_ids = set()
        for a in raw:
            resolved = _resolve_status(a)
            if resolved['has_any_punch']:
                punched_ids.add(a.employee_id)

        absent_employees = [e for e in all_employees if e.id not in punched_ids]
        return [e.to_dict() for e in absent_employees] 

