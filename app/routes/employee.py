"""Employee self-service routes: dashboard, overtime, leave, summary"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from datetime import date, datetime, time
from types import SimpleNamespace

from app.models import Employee, SystemLog
from app.models.attendance import Attendance
from app.models.time_off import OvertimeRequest, LeaveRequest, AttendanceCorrectionRequest
from app.utils.time_off_utils import is_at_least_days_ahead
from app.utils.timezone_utils import to_local, format_time_input


bp = Blueprint('employee', __name__, url_prefix='/employee')


def _has_leave_conflict(employee_id, target_date):
    return LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_(['pending', 'approved']),
        LeaveRequest.start_date <= target_date,
        LeaveRequest.end_date >= target_date
    ).first() is not None


def _has_overtime_conflict(employee_id, start_date, end_date):
    return OvertimeRequest.query.filter(
        OvertimeRequest.employee_id == employee_id,
        OvertimeRequest.status.in_(['pending', 'approved']),
        OvertimeRequest.date >= start_date,
        OvertimeRequest.date <= end_date
    ).first() is not None


def _withdraw_time_off_request(request_obj, employee, redirect_endpoint, success_message, log_action):
    if request_obj.employee_id != employee.id:
        flash('Bạn không có quyền thu hồi yêu cầu này.', 'danger')
        return redirect(url_for(redirect_endpoint))

    if request_obj.status != 'pending':
        flash('Chỉ có thể thu hồi yêu cầu đang chờ duyệt.', 'warning')
        return redirect(url_for(redirect_endpoint))

    request_obj.status = 'withdrawn'
    request_obj.admin_note = None
    db.session.commit()

    SystemLog.log_action(
        user_id=current_user.id,
        action=log_action,
        entity_type='employee',
        entity_id=employee.id,
        details=f'{employee.name} đã thu hồi yêu cầu #{request_obj.id}.',
        status='success'
    )

    flash(success_message, 'success')
    return redirect(url_for(redirect_endpoint))


def _get_employee_for_user():
    """Attempt to resolve an Employee for the logged-in `current_user`.

    Strategy:
    - Match by email
    - Fallback: match User.username to employee_code
    """
    if not current_user or not getattr(current_user, 'is_authenticated', False):
        return None

    # Try by email
    emp = None
    try:
        emp = Employee.query.filter_by(email=current_user.email, is_active=True).first()
    except Exception:
        emp = None

    if emp:
        return emp

    # Fallback: use username as employee_code
    try:
        emp = Employee.query.filter_by(employee_code=getattr(current_user, 'username', None), is_active=True).first()
    except Exception:
        emp = None

    return emp


@bp.route('')
@bp.route('/')
def home():
    return redirect(url_for('employee.dashboard'))


@bp.route('/dashboard')
@login_required
def dashboard():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy bản ghi nhân viên tương ứng. Vui lòng liên hệ quản trị viên để đồng bộ thông tin.', 'warning')
        emp = SimpleNamespace(
            id=None,
            name=getattr(current_user, 'name', None) or getattr(current_user, 'username', 'Nhân viên'),
            employee_code=getattr(current_user, 'username', 'N/A')
        )
        return render_template('employee/dashboard.html', employee=emp,
                               total_days=0,
                               total_working_hours=0,
                               total_overtime=0,
                               total_points=0,
                               attendances=[])

    today = date.today()
    month_start = date(today.year, today.month, 1)
    # get attendances for current month
    attendances = Attendance.query.filter(
        Attendance.employee_id == emp.id,
        Attendance.date >= month_start
    ).all()
    # Only include attendances where the employee actually worked (not absent)
    # or where admin has recorded overtime check-in/out (i.e., actual OT happened).
    visible_attendances = []
    for a in attendances:
        # Determine whether this attendance contains actual OT punches.
        has_actual_ot = False
        try:
            if a.overtime_check_in_time and a.overtime_check_out_time:
                # If OT timestamps differ from the default approval window (17:30-20:00)
                # treat as actual OT. Also treat as actual OT if regular punches exist.
                default_start = datetime.combine(a.date, time(17, 30))
                default_end = datetime.combine(a.date, time(20, 0))
                no_regular_punches = not any([a.check_in_time, a.check_out_time, a.check_in_time_2, a.check_out_time_2])
                is_default_window = (a.overtime_check_in_time == default_start and a.overtime_check_out_time == default_end)
                if (not is_default_window) or (not no_regular_punches):
                    has_actual_ot = True
        except Exception:
            has_actual_ot = False

        if a.status != 'absent' or has_actual_ot:
            visible_attendances.append(a)

    total_days = sum(1 for a in visible_attendances if a.status != 'absent')
    total_working_hours = round(sum((a.working_hours or 0) for a in visible_attendances), 2)
    total_overtime = round(sum((a.overtime_hours or 0) for a in visible_attendances), 2)
    # Total points = administrative working hours + overtime points (as used in admin exports)
    total_points = round(sum(((a.working_hours or 0) + (a.overtime_hours or 0)) for a in visible_attendances), 2)

    return render_template('employee/dashboard.html', employee=emp,
                           total_days=total_days,
                           total_working_hours=total_working_hours,
                           total_overtime=total_overtime,
                           total_points=total_points,
                           attendances=visible_attendances)


@bp.route('/attendance/history')
@login_required
def attendance_history():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    # optional month/year params
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    today = date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month

    start = date(year, month, 1)
    # compute end of month (simple approach)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    attendances = Attendance.query.filter(
        Attendance.employee_id == emp.id,
        Attendance.date >= start,
        Attendance.date < end
    ).order_by(Attendance.date).all()

    # Filter out absent records that only have a scheduled OT request (no actual OT timestamps).
    visible_attendances = []
    for a in attendances:
        has_actual_ot = False
        try:
            if a.overtime_check_in_time and a.overtime_check_out_time:
                default_start = datetime.combine(a.date, time(17, 30))
                default_end = datetime.combine(a.date, time(20, 0))
                no_regular_punches = not any([a.check_in_time, a.check_out_time, a.check_in_time_2, a.check_out_time_2])
                is_default_window = (a.overtime_check_in_time == default_start and a.overtime_check_out_time == default_end)
                if (not is_default_window) or (not no_regular_punches):
                    has_actual_ot = True
        except Exception:
            has_actual_ot = False

        if a.status != 'absent' or has_actual_ot:
            visible_attendances.append(a)

    return render_template('employee/attendance_history.html', employee=emp, attendances=visible_attendances, year=year, month=month)


@bp.route('/profile')
@login_required
def profile():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    return render_template('employee/profile.html', employee=emp)


@bp.route('/attendance')
@login_required
def attendance():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    return redirect(url_for('kiosk.attendance_only'))


@bp.route('/overtime', methods=['GET', 'POST'])
@login_required
def overtime():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    if request.method == 'POST':
        req_date = request.form.get('date')
        request_type = request.form.get('request_type', 'overtime')
        reason = request.form.get('reason')
        try:
            dt = datetime.strptime(req_date, '%Y-%m-%d').date()
        except Exception:
            flash('Ngày không hợp lệ. Vui lòng dùng định dạng YYYY-MM-DD.', 'danger')
            return redirect(url_for('employee.overtime'))

        if not is_at_least_days_ahead(dt, minimum_days=1):
            flash('Yêu cầu tăng ca phải được đăng ký trước ít nhất 1 ngày.', 'danger')
            return redirect(url_for('employee.overtime'))

        if request_type == 'sunday':
            if dt.weekday() != 6:
                flash('Vui lòng chọn ngày Chủ nhật để đăng ký làm Chủ nhật.', 'danger')
                return redirect(url_for('employee.overtime'))
            hours = 8.0
            reason = reason or 'Đăng ký làm Chủ nhật'
        else:
            if dt.weekday() == 6:
                flash('Ngày Chủ nhật phải đăng ký bằng lựa chọn "Làm Chủ nhật".', 'danger')
                return redirect(url_for('employee.overtime'))
            hours = 2.5
            reason = reason or 'Tăng ca 17:30 - 20:00'

        if _has_leave_conflict(emp.id, dt):
            flash('Không thể đăng ký tăng ca cho ngày đã có yêu cầu xin nghỉ.', 'danger')
            return redirect(url_for('employee.overtime'))

        # Prevent duplicate requests for same date
        existing_ot = OvertimeRequest.query.filter_by(employee_id=emp.id, date=dt).filter(OvertimeRequest.status.in_(['pending', 'approved'])).first()
        if existing_ot:
            flash('Đã có yêu cầu tăng ca hoặc làm Chủ nhật cho ngày này.', 'warning')
            return redirect(url_for('employee.overtime'))

        o = OvertimeRequest(employee_id=emp.id, date=dt, hours=hours, reason=reason, status='pending')
        db.session.add(o)
        db.session.commit()
        flash('Yêu cầu đã được gửi.', 'success')
        return redirect(url_for('employee.overtime'))

    requests = OvertimeRequest.query.filter_by(employee_id=emp.id).order_by(OvertimeRequest.created_at.desc()).all()
    return render_template('employee/overtime.html', employee=emp, requests=requests)


@bp.route('/overtime/<int:request_id>/withdraw', methods=['POST'])
@login_required
def withdraw_overtime(request_id: int):
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    req = OvertimeRequest.query.get_or_404(request_id)
    return _withdraw_time_off_request(
        req,
        emp,
        'employee.overtime',
        'Đã thu hồi yêu cầu tăng ca.',
        'employee_withdrew_overtime_request'
    )


@bp.route('/leave', methods=['GET', 'POST'])
@login_required
def leave():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
        except Exception:
            flash('Ngày không hợp lệ. Vui lòng dùng định dạng YYYY-MM-DD.', 'danger')
            return redirect(url_for('employee.leave'))

        if not is_at_least_days_ahead(sd, minimum_days=1):
            flash('Yêu cầu xin nghỉ phải được gửi trước ít nhất 1 ngày.', 'danger')
            return redirect(url_for('employee.leave'))

        # Validation
        if sd > ed:
            flash('Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.', 'danger')
            return redirect(url_for('employee.leave'))

        # Prevent overlapping leave requests (pending or approved)
        overlap = LeaveRequest.query.filter(
            LeaveRequest.employee_id == emp.id,
            LeaveRequest.start_date <= ed,
            LeaveRequest.end_date >= sd,
            LeaveRequest.status.in_(['pending', 'approved'])
        ).first()
        if overlap:
            flash('Đã có yêu cầu nghỉ trùng khoảng ngày bạn nhập (đã gửi hoặc đã duyệt).', 'warning')
            return redirect(url_for('employee.leave'))

        if _has_overtime_conflict(emp.id, sd, ed):
            flash('Không thể xin nghỉ vì đã có yêu cầu tăng ca trong khoảng ngày này.', 'danger')
            return redirect(url_for('employee.leave'))

        # Prevent requesting leave in the past
        today = date.today()
        if ed < today:
            flash('Không thể yêu cầu nghỉ cho khoảng đã qua.', 'danger')
            return redirect(url_for('employee.leave'))

        l = LeaveRequest(employee_id=emp.id, start_date=sd, end_date=ed, reason=reason, status='pending')
        db.session.add(l)
        db.session.commit()
        flash('Yêu cầu xin nghỉ đã được gửi.', 'success')
        return redirect(url_for('employee.leave'))

    requests = LeaveRequest.query.filter_by(employee_id=emp.id).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('employee/leave.html', employee=emp, requests=requests)


@bp.route('/leave/<int:request_id>/withdraw', methods=['POST'])
@login_required
def withdraw_leave(request_id: int):
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    req = LeaveRequest.query.get_or_404(request_id)
    return _withdraw_time_off_request(
        req,
        emp,
        'employee.leave',
        'Đã thu hồi yêu cầu xin nghỉ.',
        'employee_withdrew_leave_request'
    )


# ========== ATTENDANCE CORRECTION ==========

REASON_TYPE_OPTIONS = [
    ('missing_check_in', 'Thiếu check-in'),
    ('missing_check_out', 'Thiếu check-out'),
    ('wrong_time', 'Sai giờ'),
    ('absent_correction', 'Bổ sung vắng mặt'),
    ('other', 'Lý do khác'),
]


def _has_correction_conflict(employee_id, target_date):
    return AttendanceCorrectionRequest.query.filter(
        AttendanceCorrectionRequest.employee_id == employee_id,
        AttendanceCorrectionRequest.date == target_date,
        AttendanceCorrectionRequest.status.in_(['pending', 'approved'])
    ).first() is not None


@bp.route('/attendance-correction', methods=['GET', 'POST'])
@login_required
def attendance_correction():
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    if request.method == 'POST':
        req_date = request.form.get('date')
        reason_type = request.form.get('reason_type')
        explanation = request.form.get('explanation', '').strip()

        try:
            dt = datetime.strptime(req_date, '%Y-%m-%d').date()
        except Exception:
            flash('Ngày không hợp lệ. Vui lòng dùng định dạng YYYY-MM-DD.', 'danger')
            return redirect(url_for('employee.attendance_correction'))

        # Chỉ cho yêu cầu cho ngày trong quá khứ (tối đa 7 ngày)
        today = date.today()
        if dt >= today:
            flash('Chỉ có thể gửi yêu cầu bổ sung/chỉnh sửa cho ngày trong quá khứ.', 'danger')
            return redirect(url_for('employee.attendance_correction'))

        if dt < today - __import__('datetime').timedelta(days=7):
            flash('Chỉ có thể gửi yêu cầu cho tối đa 7 ngày gần đây.', 'danger')
            return redirect(url_for('employee.attendance_correction'))

        if reason_type not in [r[0] for r in REASON_TYPE_OPTIONS]:
            flash('Loại yêu cầu không hợp lệ.', 'danger')
            return redirect(url_for('employee.attendance_correction'))

        # Kiểm tra trùng lặp
        if _has_correction_conflict(emp.id, dt):
            flash('Đã có yêu cầu bổ sung/chỉnh sửa đang chờ duyệt hoặc đã duyệt cho ngày này.', 'warning')
            return redirect(url_for('employee.attendance_correction'))

        # Kiểm tra leave request approved trùng ngày
        if _has_leave_conflict(emp.id, dt):
            flash('Không thể gửi yêu cầu bổ sung chấm công cho ngày đã có yêu cầu xin nghỉ.', 'danger')
            return redirect(url_for('employee.attendance_correction'))

        # Parse giờ (optional)
        check_in_time = None
        check_out_time = None
        check_in_time_2 = None
        check_out_time_2 = None

        check_in_str = request.form.get('check_in_time', '').strip()
        check_out_str = request.form.get('check_out_time', '').strip()
        check_in_2_str = request.form.get('check_in_time_2', '').strip()
        check_out_2_str = request.form.get('check_out_time_2', '').strip()

        if check_in_str:
            try:
                check_in_time = to_local(datetime.strptime(f"{req_date} {check_in_str}", '%Y-%m-%d %H:%M'))
            except ValueError:
                flash('Giờ check-in không hợp lệ.', 'danger')
                return redirect(url_for('employee.attendance_correction'))

        if check_out_str:
            try:
                check_out_time = to_local(datetime.strptime(f"{req_date} {check_out_str}", '%Y-%m-%d %H:%M'))
            except ValueError:
                flash('Giờ check-out không hợp lệ.', 'danger')
                return redirect(url_for('employee.attendance_correction'))

        if check_in_2_str:
            try:
                check_in_time_2 = to_local(datetime.strptime(f"{req_date} {check_in_2_str}", '%Y-%m-%d %H:%M'))
            except ValueError:
                flash('Giờ check-in 2 không hợp lệ.', 'danger')
                return redirect(url_for('employee.attendance_correction'))

        if check_out_2_str:
            try:
                check_out_time_2 = to_local(datetime.strptime(f"{req_date} {check_out_2_str}", '%Y-%m-%d %H:%M'))
            except ValueError:
                flash('Giờ check-out 2 không hợp lệ.', 'danger')
                return redirect(url_for('employee.attendance_correction'))

        correction = AttendanceCorrectionRequest(
            employee_id=emp.id,
            date=dt,
            reason_type=reason_type,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            check_in_time_2=check_in_time_2,
            check_out_time_2=check_out_time_2,
            explanation=explanation,
            status='pending',
        )
        db.session.add(correction)
        db.session.commit()

        SystemLog.log_action(
            user_id=current_user.id,
            action='employee_submitted_correction',
            entity_type='employee',
            entity_id=emp.id,
            details=f'{emp.name} gửi yêu cầu bổ sung chấm công ngày {dt}.',
            status='success'
        )

        flash('Yêu cầu bổ sung chấm công đã được gửi.', 'success')
        return redirect(url_for('employee.attendance_correction'))

    # GET: form + lịch sử
    requests = AttendanceCorrectionRequest.query.filter_by(
        employee_id=emp.id
    ).order_by(AttendanceCorrectionRequest.created_at.desc()).all()

    # Lấy giờ chấm công hiện tại của ngày đang chọn (dùng JS hoặc query gần nhất)
    return render_template('employee/attendance_correction.html',
                           employee=emp,
                           requests=requests,
                           reason_types=REASON_TYPE_OPTIONS,
                           today=date.today(),
                           timedelta=__import__('datetime').timedelta)


@bp.route('/attendance-correction/<int:correction_id>/withdraw', methods=['POST'])
@login_required
def withdraw_correction(correction_id: int):
    emp = _get_employee_for_user()
    if not emp:
        flash('Không tìm thấy thông tin nhân viên cho tài khoản hiện tại.', 'warning')
        return redirect(url_for('kiosk.attendance_only'))

    correction = AttendanceCorrectionRequest.query.get_or_404(correction_id)
    return _withdraw_time_off_request(
        correction,
        emp,
        'employee.attendance_correction',
        'Đã thu hồi yêu cầu bổ sung chấm công.',
        'employee_withdrew_correction_request'
    )


@bp.route('/summary')
@login_required
def summary():
    # simple alias to dashboard for now
    return redirect(url_for('employee.dashboard'))
