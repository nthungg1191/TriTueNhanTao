"""Admin dashboard routes"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import subqueryload
from app import db
from app.models import Employee, Attendance, Department, WorkSchedule, User
from app.models.time_off import OvertimeRequest, LeaveRequest, AttendanceCorrectionRequest
from app.services.notification_service import NotificationService
from datetime import date, datetime, time, timedelta
import os
import re
import uuid
import cv2
import numpy as np
from sqlalchemy.exc import IntegrityError
from app.utils.timezone_utils import get_local_now, to_local, format_time_input
# Lazy-import face services inside functions to avoid import-time errors

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/requests')
@login_required
def requests():
    """View pending overtime, leave and correction requests for admin to approve/reject"""
    # Filters from query string
    kind = request.args.get('kind', 'all')
    start_date = _parse_date_string(request.args.get('start_date'))
    end_date = _parse_date_string(request.args.get('end_date'))

    overtime_requests = []
    leave_requests = []
    correction_requests = []

    if kind in ('all', 'overtime'):
        q = OvertimeRequest.query
        if start_date:
            q = q.filter(OvertimeRequest.date >= start_date)
        if end_date:
            q = q.filter(OvertimeRequest.date <= end_date)
        overtime_requests = q.order_by(OvertimeRequest.created_at.desc()).all()

    if kind in ('all', 'leave'):
        q2 = LeaveRequest.query
        if start_date:
            q2 = q2.filter(LeaveRequest.start_date >= start_date)
        if end_date:
            q2 = q2.filter(LeaveRequest.end_date <= end_date)
        leave_requests = q2.order_by(LeaveRequest.created_at.desc()).all()

    if kind in ('all', 'correction'):
        q3 = AttendanceCorrectionRequest.query
        if start_date:
            q3 = q3.filter(AttendanceCorrectionRequest.date >= start_date)
        if end_date:
            q3 = q3.filter(AttendanceCorrectionRequest.date <= end_date)
        correction_requests = q3.order_by(AttendanceCorrectionRequest.created_at.desc()).all()

    return render_template('admin/requests.html',
                           overtime_requests=overtime_requests,
                           leave_requests=leave_requests,
                           correction_requests=correction_requests)


@bp.route('/requests/<string:kind>/<int:request_id>')
@login_required
def request_detail(kind: str, request_id: int):
    """Show detail for a specific request and allow admin to add note on review."""
    if kind == 'overtime':
        req = OvertimeRequest.query.get_or_404(request_id)
    elif kind == 'correction':
        req = AttendanceCorrectionRequest.query.get_or_404(request_id)
    else:
        req = LeaveRequest.query.get_or_404(request_id)

    return render_template('admin/request_detail.html', kind=kind, request=req)


@bp.route('/requests/overtime/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_overtime(request_id: int):
    req = OvertimeRequest.query.get_or_404(request_id)
    if req.status == 'cancelled':
        flash('Yêu cầu này đã bị quá hạn tự động.', 'warning')
        return redirect(url_for('admin.requests'))
    req.status = 'approved'
    req.reviewer_id = current_user.id
    req.reviewed_at = get_local_now()
    # Ensure an Attendance record exists for that employee/date and set default OT window (17:30-20:00)
    try:
        attendance = Attendance.query.filter_by(employee_id=req.employee_id, date=req.date).first()
        ot_start = datetime.combine(req.date, time(17, 30))
        # default end 20:00 or derive from requested hours if longer
        ot_end = datetime.combine(req.date, time(20, 0))
        if req.hours and req.hours > 0:
            requested_end = ot_start + timedelta(hours=req.hours)
            # don't extend beyond 23:59
            if requested_end.time() > time(23, 59):
                requested_end = datetime.combine(req.date, time(23, 59))
            # prefer requested end if it is after default end
            if requested_end > ot_end:
                ot_end = requested_end

        if not attendance:
            # Create an attendance row but DO NOT populate OT timestamps here.
            # OT timestamps should only be set when actual punches or admin-entered
            # OT check-in/out times are available.
            attendance = Attendance(
                employee_id=req.employee_id,
                employee=req.employee,
                date=req.date,
                working_hours=0.0,
                overtime_hours=0.0
            )
            db.session.add(attendance)
        else:
            # If this attendance already has OT timestamps that were auto-filled
            # by a previous approval (default window 17:30-20:00) but there are
            # no actual punches recorded, clear those OT timestamps so the day
            # does not appear on the employee dashboard until real OT occurs.
            try:
                from datetime import time as _time
                ot_ci = attendance.overtime_check_in_time
                ot_co = attendance.overtime_check_out_time
                no_punches = not any([attendance.check_in_time, attendance.check_out_time, attendance.check_in_time_2, attendance.check_out_time_2])
                if ot_ci and ot_co and no_punches:
                    if ot_ci.time() == _time(17, 30) and ot_co.time() == _time(20, 0):
                        attendance.overtime_check_in_time = None
                        attendance.overtime_check_out_time = None
                        attendance.overtime_hours = 0.0
            except Exception:
                # don't block approval on cleanup errors
                pass

        # Recalculate working and overtime hours using model logic
        try:
            attendance.calculate_working_hours()
            attendance.update_status()
        except Exception:
            db.session.rollback()
            raise

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    # send notification
    NotificationService.send_notification(req.employee_id, 'overtime_approved', f'Yêu cầu tăng ca ngày {req.date} đã được duyệt.')
    flash('Đã duyệt yêu cầu tăng ca.', 'success')
    return redirect(url_for('admin.requests'))


@bp.route('/requests/overtime/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_overtime(request_id: int):
    req = OvertimeRequest.query.get_or_404(request_id)
    if req.status == 'cancelled':
        flash('Yêu cầu này đã bị quá hạn tự động.', 'warning')
        return redirect(url_for('admin.requests'))
    admin_note = request.form.get('admin_note')
    req.status = 'rejected'
    req.admin_note = admin_note
    req.reviewer_id = current_user.id
    req.reviewed_at = get_local_now()
    db.session.commit()
    NotificationService.send_notification(req.employee_id, 'overtime_rejected', f'Yêu cầu tăng ca ngày {req.date} bị từ chối. Lý do: {admin_note or "Không có"}')
    flash('Đã từ chối yêu cầu tăng ca.', 'info')
    return redirect(url_for('admin.requests'))


@bp.route('/requests/leave/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_leave(request_id: int):
    req = LeaveRequest.query.get_or_404(request_id)
    if req.status == 'cancelled':
        flash('Yêu cầu này đã bị quá hạn tự động.', 'warning')
        return redirect(url_for('admin.requests'))
    req.status = 'approved'
    req.reviewer_id = current_user.id
    req.reviewed_at = get_local_now()
    # Auto-reject any pending overtime requests that overlap with approved leave
    try:
        OvertimeRequest.query.filter(
            OvertimeRequest.employee_id == req.employee_id,
            OvertimeRequest.date >= req.start_date,
            OvertimeRequest.date <= req.end_date,
            OvertimeRequest.status == 'pending'
        ).update({'status': 'rejected'})
    except Exception:
        db.session.rollback()
        raise

    db.session.commit()
    NotificationService.send_notification(req.employee_id, 'leave_approved', f'Yêu cầu xin nghỉ {req.start_date} -> {req.end_date} đã được duyệt.')
    flash('Đã duyệt yêu cầu xin nghỉ.', 'success')
    return redirect(url_for('admin.requests'))


@bp.route('/requests/leave/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_leave(request_id: int):
    req = LeaveRequest.query.get_or_404(request_id)
    if req.status == 'cancelled':
        flash('Yêu cầu này đã bị quá hạn tự động.', 'warning')
        return redirect(url_for('admin.requests'))
    admin_note = request.form.get('admin_note')
    req.status = 'rejected'
    req.admin_note = admin_note
    req.reviewer_id = current_user.id
    req.reviewed_at = get_local_now()
    db.session.commit()
    NotificationService.send_notification(req.employee_id, 'leave_rejected', f'Yêu cầu xin nghỉ {req.start_date} -> {req.end_date} bị từ chối. Lý do: {admin_note or "Không có"}')
    flash('Đã từ chối yêu cầu xin nghỉ.', 'info')
    return redirect(url_for('admin.requests'))


# ========== ATTENDANCE CORRECTION ==========

@bp.route('/requests/attendance-correction/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_correction(request_id: int):
    req = AttendanceCorrectionRequest.query.get_or_404(request_id)

    req.status = 'approved'
    req.reviewer_id = current_user.id
    req.reviewed_at = get_local_now()
    admin_note = request.form.get('admin_note', '').strip()
    if admin_note:
        req.admin_note = admin_note

    try:
        # Tạo/cập nhật bản Attendance cho employee_id + date
        attendance = Attendance.query.filter_by(employee_id=req.employee_id, date=req.date).first()

        if not attendance:
            attendance = Attendance(
                employee_id=req.employee_id,
                employee=req.employee,
                date=req.date,
                working_hours=0.0,
                overtime_hours=0.0,
            )
            db.session.add(attendance)

        # Gán các giờ check-in/out từ yêu cầu (chỉ ghi đè nếu có giá trị)
        if req.check_in_time:
            attendance.check_in_time = req.check_in_time
        if req.check_out_time:
            attendance.check_out_time = req.check_out_time
        if req.check_in_time_2:
            attendance.check_in_time_2 = req.check_in_time_2
        if req.check_out_time_2:
            attendance.check_out_time_2 = req.check_out_time_2

        attendance.calculate_working_hours()
        attendance.update_status()

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    NotificationService.send_notification(
        req.employee_id, 'correction_approved',
        f'Yêu cầu bổ sung chấm công ngày {req.date} đã được duyệt.'
    )
    flash('Đã duyệt yêu cầu bổ sung chấm công và cập nhật bản ghi chấm công.', 'success')
    return redirect(url_for('admin.requests'))


@bp.route('/requests/attendance-correction/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_correction(request_id: int):
    req = AttendanceCorrectionRequest.query.get_or_404(request_id)
    admin_note = request.form.get('admin_note')
    req.status = 'rejected'
    req.admin_note = admin_note
    req.reviewer_id = current_user.id
    req.reviewed_at = get_local_now()
    db.session.commit()
    NotificationService.send_notification(
        req.employee_id, 'correction_rejected',
        f'Yêu cầu bổ sung chấm công ngày {req.date} bị từ chối. Lý do: {admin_note or "Không có"}'
    )
    flash('Đã từ chối yêu cầu bổ sung chấm công.', 'info')
    return redirect(url_for('admin.requests'))


def _save_employee_photo(file_storage):
    """Save employee photo and return (photo_path, image_array, error_message)."""
    if not file_storage or not getattr(file_storage, 'filename', ''):
        return None, None, None

    photo_bytes = file_storage.read()
    if not photo_bytes:
        return None, None, 'Ảnh nhân viên rỗng hoặc không hợp lệ.'

    np_buffer = np.frombuffer(photo_bytes, np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if image is None:
        return None, None, 'Không thể đọc ảnh nhân viên. Vui lòng chọn ảnh hợp lệ.'

    upload_dir = os.path.join(current_app.config['UPLOAD_PATH'], 'employees')
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"employee_{uuid.uuid4().hex}.jpg"
    full_path = os.path.join(upload_dir, filename)
    cv2.imwrite(full_path, image)

    return f"/static/uploads/employees/{filename}", image, None


def _register_face_from_employee_photo(employee_code: str, image: np.ndarray, photo_path: str = None, skip_employee_code: str = None):
    """Generate face encoding from employee photo and upsert embeddings.

    Args:
        skip_employee_code: When set, exclude this employee_code from the
            duplicate-face check (used during employee edit to allow re-uploading
            the same person's photo).
    """
    try:
        from app.services.face_detection import FaceDetector
        from app.services.face_service import FaceService
    except Exception as e:
        return False, f'Không thể khởi tạo dịch vụ nhận diện: {e}'

    detector = FaceDetector()
    detect_result = detector.process_image(image)

    if detect_result['faces_found'] == 0:
        return False, 'Ảnh nhân viên không có khuôn mặt nên chưa thể bật nhận diện chấm công.'

    if detect_result['faces_found'] > 1:
        return False, 'Ảnh nhân viên có nhiều khuôn mặt. Vui lòng dùng ảnh chỉ có 1 khuôn mặt.'

    face_encoding = detect_result['face_encodings'][0]
    face_service = FaceService(db.session)

    # --- Duplicate face check ---
    try:
        recognition = face_service.recognize_employee_multi(face_encoding, use_multi_embedding=True)
        if recognition.get('success') and recognition.get('employee_code'):
            matched_code = recognition['employee_code']
            if matched_code != employee_code:
                matched_name = recognition.get('employee_name', matched_code)
                return False, (
                    f'Khuôn mặt này đã thuộc về nhân viên '
                    f'"{matched_name}" ({matched_code}). '
                    f'Không thể đăng ký cho nhân viên khác.'
                )
            # matched_code == employee_code → same employee, allowed
    except Exception:
        pass  # If recognition check fails, proceed with registration

    legacy_result = face_service.register_employee_face(
        employee_code=employee_code,
        face_encoding=face_encoding,
        image_path=photo_path
    )
    if not legacy_result.get('success'):
        return False, legacy_result.get('message', 'Không thể lưu face encoding (legacy).')

    embedding_result = face_service.add_face_embedding(
        employee_code=employee_code,
        embedding=face_encoding,
        variant_type='default',
        embedding_type='standard',
        description='Auto-generated from employee profile photo',
        photo_path=photo_path,
        set_as_primary=True
    )
    if not embedding_result.get('success'):
        return False, embedding_result.get('message', 'Không thể lưu face embedding.')

    return True, 'Đã cập nhật ảnh mặc định cho nhận diện (giữ nguyên bộ 3 góc nếu đã có).'


def _generate_next_employee_code(prefix='NV', width=3):
    """Generate the next employee code based on existing values."""
    existing_codes = [code for (code,) in db.session.query(Employee.employee_code).all() if code]
    max_number = 0
    for code in existing_codes:
        match = re.search(r'(\d+)$', code)
        if match:
            try:
                max_number = max(max_number, int(match.group(1)))
            except ValueError:
                continue
    return f"{prefix}{max_number + 1:0{width}d}"


def _sync_employee_user(employee, password=None, old_username=None):
    """Create or update the corresponding User account for an employee."""
    username = employee.employee_code
    email = employee.email or f"{username.lower()}@example.com"
    user = None

    if old_username:
        user = User.query.filter_by(username=old_username).first()
        if user and old_username != username:
            user.username = username

    if not user:
        user = User.query.filter_by(username=username).first()

    if not user:
        user = User(
            username=username,
            email=email,
            role='employee',
            is_active=employee.is_active
        )
        db.session.add(user)
    else:
        user.email = email
        user.is_active = employee.is_active

    if password:
        user.set_password(password)
    elif not user.password_hash:
        user.set_password(username.lower())

    db.session.commit()
    return user


def _parse_date_string(value):
    """Parse a date value from dd/mm/yyyy or yyyy-mm-dd."""
    if not value:
        return None
    value = value.strip()
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_local_datetime(value):
    """Parse a datetime-local input (YYYY-MM-DDTHH:MM) and attach local timezone."""
    if not value:
        return None
    try:
        dt = datetime.strptime(value.strip(), '%Y-%m-%dT%H:%M')
        return to_local(dt)
    except ValueError:
        return None


@bp.before_request
def require_admin():
    """Ensure only admin users access admin routes."""
    # Allow static files or other non-view requests through
    from flask import redirect, url_for, request, flash
    from flask_login import current_user

    # If not authenticated, redirect to login with next
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))

    # If authenticated but not admin, redirect to kiosk with message
    if getattr(current_user, 'role', None) != 'admin':
        flash('Bạn không có quyền truy cập trang quản trị', 'danger')
        return redirect(url_for('kiosk.attendance_only'))
    
    # Check if migration is needed (skip for migration pages)
    if request.endpoint and 'migrate' not in request.endpoint:
        try:
            from app.models.face_embedding import FaceEmbedding
            legacy_count = Employee.query.filter(
                Employee.face_encoding.isnot(None)
            ).count()
            
            if legacy_count > 0:
                multi_count = db.session.query(FaceEmbedding).count()
                if legacy_count > multi_count:
                    flash(
                        f'⚠️ Phát hiện {legacy_count} khuôn mặt legacy cần migration. '
                        f'<a href="{url_for("admin.migrate_face_encodings")}" class="alert-link">Click để migrate ngay</a>',
                        'warning'
                    )
        except Exception:
            pass  # Ignore errors in check


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    from app.services.reports_service import ReportsService
    from app.services.notification_service import NotificationService
    
    # Get statistics
    total_employees = Employee.query.filter_by(is_active=True).count()
    today = date.today()
    
    # Get today's report
    today_report = ReportsService.get_daily_report(today)
    
    # Get weekly report
    weekly_report = ReportsService.get_weekly_report()
    
    # Get late employees
    late_employees = ReportsService.get_late_employees(today, limit=5)
    
    # Get absent employees
    absent_employees = ReportsService.get_absent_employees(today)
    
    # Get dashboard alerts
    alerts = NotificationService.get_dashboard_alerts()
    
    return render_template('admin/dashboard.html',
                         total_employees=total_employees,
                         today_report=today_report,
                         weekly_report=weekly_report,
                         late_employees=late_employees,
                         absent_employees=absent_employees,
                         alerts=alerts)


@bp.route('/employees')
@login_required
def employees():
    """Employee management page"""
    employees = Employee.query.options(
        subqueryload(Employee.face_embeddings)
    ).filter_by(is_active=True).order_by(Employee.created_at.desc()).all()
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    return render_template('admin/employees.html', 
                         employees=employees,
                         departments=departments)


# Employee CRUD
@bp.route('/employees/new', methods=['GET', 'POST'])
@login_required
def employee_new():
    if request.method == 'POST':
        try:
            employee_code = request.form.get('employee_code', '').strip()
            if not employee_code:
                employee_code = _generate_next_employee_code()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            password_min_length = current_app.config.get('PASSWORD_MIN_LENGTH', 8)
            
            if not employee_code or not name:
                flash('Mã nhân viên và tên nhân viên là bắt buộc.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=None,
                                     departments=departments,
                                     new_employee_code=employee_code)

            if password or confirm_password:
                if password != confirm_password:
                    flash('Mật khẩu và xác nhận mật khẩu không khớp.', 'danger')
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    return render_template('admin/employee_form.html', 
                                         employee=None,
                                         departments=departments,
                                         new_employee_code=employee_code)
                if len(password) < password_min_length:
                    flash(f'Mật khẩu phải có ít nhất {password_min_length} ký tự.', 'danger')
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    return render_template('admin/employee_form.html', 
                                         employee=None,
                                         departments=departments,
                                         new_employee_code=employee_code)

            existing_emp = Employee.query.filter_by(employee_code=employee_code).first()
            if existing_emp:
                flash('Mã nhân viên đã tồn tại. Vui lòng dùng mã khác.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=None,
                                     departments=departments,
                                     new_employee_code=_generate_next_employee_code())

            if email:
                existing_email = Employee.query.filter_by(email=email).first()
                if existing_email:
                    flash('Email này đã được dùng cho nhân viên khác. Vui lòng sử dụng email khác.', 'danger')
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    return render_template('admin/employee_form.html', 
                                         employee=None,
                                         departments=departments,
                                         new_employee_code=employee_code)
                existing_user_email = User.query.filter_by(email=email).first()
                if existing_user_email:
                    flash('Email này đã được dùng cho tài khoản khác. Vui lòng sử dụng email khác.', 'danger')
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    return render_template('admin/employee_form.html', 
                                         employee=None,
                                         departments=departments,
                                         new_employee_code=employee_code)
            # Validate phone: only digits, 10 chars, valid VN mobile prefixes
            if phone:
                import re
                phone_pattern = re.compile(r'^(03|05|07|08|09)\d{8}$')
                if not phone_pattern.match(phone):
                    flash('Số điện thoại không hợp lệ. Vui lòng nhập 10 chữ số bắt đầu bằng 03,05,07,08 hoặc 09.', 'danger')
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    return render_template('admin/employee_form.html', 
                                         employee=None,
                                         departments=departments,
                                         new_employee_code=employee_code)
            
            # NEW: Dùng department_id thay vì department string
            department_id = request.form.get('department_id')
            if department_id:
                try:
                    department_id = int(department_id)
                except (ValueError, TypeError):
                    department_id = None
            else:
                department_id = None
            
            position = request.form.get('position', '').strip() or None
            hire_date = _parse_date_string(request.form.get('hire_date', '').strip())
            notes = request.form.get('notes', '').strip() or None
            is_active = request.form.get('is_active') == 'on'

            emp = Employee(
                employee_code=employee_code,
                name=name,
                email=email,
                phone=phone,
                department_id=department_id,
                position=position,
                hire_date=hire_date,
                notes=notes,
                is_active=is_active
            )
            
            # Sync department string cho backward compatibility
            if department_id:
                dept = Department.query.get(department_id)
                if dept:
                    emp.department = dept.name
            
            db.session.add(emp)
            db.session.commit()

            _sync_employee_user(emp, password=password if password else emp.employee_code.lower())

            photo_file = request.files.get('photo')
            photo_path, image, photo_error = _save_employee_photo(photo_file)
            if photo_error:
                flash(f'Nhân viên đã tạo nhưng ảnh chưa hợp lệ: {photo_error}', 'warning')
                return redirect(url_for('admin.employee_edit', employee_id=emp.id))

            if photo_path and image is not None:
                emp.photo_path = photo_path
                db.session.commit()

                face_ok, face_message = _register_face_from_employee_photo(emp.employee_code, image, photo_path)
                flash(face_message, 'success' if face_ok else 'warning')
                return redirect(url_for('admin.employee_edit', employee_id=emp.id))

            if password:
                flash('Đã tạo nhân viên và tài khoản thành công. Tên đăng nhập là mã nhân viên.', 'success')
            else:
                flash('Đã tạo nhân viên thành công. Tài khoản nhân viên đã được tạo với mật khẩu mặc định là mã nhân viên viết thường.', 'success')
            return redirect(url_for('admin.employee_edit', employee_id=emp.id))
        except IntegrityError as e:
            db.session.rollback()
            flash('Lỗi dữ liệu trùng lặp khi tạo nhân viên. Vui lòng kiểm tra mã nhân viên và email.', 'danger')
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            return render_template('admin/employee_form.html', 
                                 employee=None,
                                 departments=departments)
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi tạo mới nhân viên: {str(e)}', 'danger')
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            return render_template('admin/employee_form.html', 
                                 employee=None,
                                 departments=departments)
    
    # GET: Show form
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    return render_template('admin/employee_form.html', 
                         employee=None,
                         departments=departments,
                         new_employee_code=_generate_next_employee_code())
@bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def employee_edit(employee_id: int):
    emp = Employee.query.get_or_404(employee_id)
    if request.method == 'POST':
        old_employee_code = emp.employee_code
        new_employee_code = request.form.get('employee_code', emp.employee_code).strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        password_min_length = current_app.config.get('PASSWORD_MIN_LENGTH', 8)

        if new_employee_code != emp.employee_code:
            existing_emp_code = Employee.query.filter(Employee.employee_code == new_employee_code, Employee.id != emp.id).first()
            if existing_emp_code:
                flash('Mã nhân viên đã tồn tại. Vui lòng dùng mã khác.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)
            existing_user_code = User.query.filter(User.username == new_employee_code).first()
            if existing_user_code and existing_user_code.username != old_employee_code:
                flash('Tên tài khoản mới đã tồn tại. Vui lòng chọn mã nhân viên khác.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)
        if password or confirm_password:
            if password != confirm_password:
                flash('Mật khẩu và xác nhận mật khẩu không khớp.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)
            if len(password) < password_min_length:
                flash(f'Mật khẩu phải có ít nhất {password_min_length} ký tự.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)

        emp.employee_code = new_employee_code
        emp.name = request.form.get('name', emp.name).strip()
        current_email = emp.email
        email = request.form.get('email', '').strip() or None
        if email and email != current_email:
            existing_email = Employee.query.filter(Employee.email == email, Employee.id != emp.id).first()
            if existing_email:
                flash('Email này đã được dùng cho nhân viên khác. Vui lòng sử dụng email khác.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)
            existing_user_email = User.query.filter(User.email == email).first()
            if existing_user_email and existing_user_email.username != old_employee_code:
                flash('Email này đã được dùng cho tài khoản khác. Vui lòng sử dụng email khác.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)
        emp.email = email
        # Validate phone on update
        new_phone = (request.form.get('phone') or '').strip() or None
        if new_phone:
            import re
            phone_pattern = re.compile(r'^(03|05|07|08|09)\d{8}$')
            if not phone_pattern.match(new_phone):
                flash('Số điện thoại không hợp lệ. Vui lòng nhập 10 chữ số bắt đầu bằng 03,05,07,08 hoặc 09.', 'danger')
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                return render_template('admin/employee_form.html', 
                                     employee=emp,
                                     departments=departments)
        emp.phone = new_phone
        
        # NEW: Dùng department_id thay vì department string
        department_id = request.form.get('department_id')
        if department_id:
            try:
                emp.department_id = int(department_id)
                # Sync department string
                dept = Department.query.get(emp.department_id)
                if dept:
                    emp.department = dept.name
            except (ValueError, TypeError):
                emp.department_id = None
                emp.department = None
        else:
            emp.department_id = None
            emp.department = None
        
        emp.position = request.form.get('position') or None
        emp.hire_date = _parse_date_string(request.form.get('hire_date', '').strip())
        emp.notes = request.form.get('notes') or None
        emp.is_active = request.form.get('is_active') == 'on'
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Lỗi dữ liệu trùng lặp khi cập nhật nhân viên. Vui lòng kiểm tra email và mã nhân viên.', 'danger')
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            return render_template('admin/employee_form.html', 
                                 employee=emp,
                                 departments=departments)

        if old_employee_code != emp.employee_code:
            from app.models.face_embedding import FaceEmbedding
            FaceEmbedding.query.filter_by(employee_id=emp.id).update({'employee_code': emp.employee_code})
            db.session.commit()

        _sync_employee_user(emp, password=password or None, old_username=old_employee_code)

        photo_file = request.files.get('photo')
        photo_path, image, photo_error = _save_employee_photo(photo_file)
        if photo_error:
            flash(f'Đã cập nhật nhân viên nhưng ảnh chưa hợp lệ: {photo_error}', 'warning')
            return redirect(url_for('admin.employee_edit', employee_id=emp.id))

        if photo_path and image is not None:
            emp.photo_path = photo_path
            db.session.commit()

            face_ok, face_message = _register_face_from_employee_photo(emp.employee_code, image, photo_path, skip_employee_code=emp.employee_code)
            flash(face_message, 'success' if face_ok else 'warning')

        flash('Cập nhật nhân viên thành công.', 'success')
        return redirect(url_for('admin.employees'))
    
    # GET: Show form
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    return render_template('admin/employee_form.html', 
                         employee=emp,
                         departments=departments)


@bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def employee_delete(employee_id: int):
    emp = Employee.query.get_or_404(employee_id)
    employee_code = emp.employee_code
    
    try:
        # Soft delete: deactivate employee instead of hard delete
        emp.is_active = False

        # Deactivate face embeddings to hide from recognition
        from app.models.face_embedding import FaceEmbedding
        FaceEmbedding.query.filter_by(employee_id=emp.id).update({'is_active': False})

        db.session.commit()

        flash(f'Đã ẩn nhân viên {employee_code}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Lỗi xóa nhân viên: {str(e)}', 'danger')
    
    return redirect(url_for('admin.employees'))


# ========== WORK SCHEDULE MANAGEMENT ==========

@bp.route('/schedules')
@login_required
def schedules():
    """Work schedule management page"""
    # Get filter parameters
    employee_id_filter = request.args.get('employee_id', type=int)
    is_active_filter = request.args.get('is_active')
    
    # Build query
    query = WorkSchedule.query
    
    if employee_id_filter:
        query = query.filter_by(employee_id=employee_id_filter)
    
    if is_active_filter is not None:
        is_active = is_active_filter.lower() == 'true'
        query = query.filter_by(is_active=is_active)
    
    # Order by employee name, then effective_from (emulate NULLS LAST for MySQL)
    # Place non-null effective_from first, then sort by effective_from desc
    schedules = query.join(Employee).order_by(
        Employee.name,
        WorkSchedule.effective_from.is_(None),
        WorkSchedule.effective_from.desc(),
        WorkSchedule.created_at.desc()
    ).all()
    
    # Get all employees for filter dropdown
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    
    # Statistics
    total_schedules = WorkSchedule.query.count()
    active_schedules = WorkSchedule.query.filter_by(is_active=True).count()
    inactive_schedules = total_schedules - active_schedules
    
    return render_template('admin/schedules.html',
                         schedules=schedules,
                         employees=employees,
                         total_schedules=total_schedules,
                         active_schedules=active_schedules,
                         inactive_schedules=inactive_schedules)


@bp.route('/schedules/new', methods=['GET', 'POST'])
@login_required
def schedule_new():
    """Create new work schedule"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        if not employee_id:
            flash('Vui lòng chọn nhân viên', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=None,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        try:
            employee_id = int(employee_id)
        except (ValueError, TypeError):
            flash('Mã nhân viên không hợp lệ', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=None,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        # Check if employee already has a work schedule
        existing_schedule = WorkSchedule.query.filter_by(employee_id=employee_id).first()
        if existing_schedule:
            flash('Nhân viên này đã có lịch làm việc. Không thể thêm lịch mới!', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=None,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        # Get shift types
        shift_types = request.form.getlist('shift_types')
        
        # Ensure regular is always selected
        if 'regular' not in shift_types:
            shift_types.append('regular')
        
        # Remove duplicates
        shift_types = list(set(shift_types))
        
        if not shift_types:
            flash('Vui lòng chọn loại ca làm việc', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=None,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        # Get work days (weekdays)
        work_days_list = request.form.getlist('work_days')
        required_days = ['0', '1', '2', '3', '4', '5']
        work_days_values = sorted(set(work_days_list + required_days), key=int)
        work_days = ','.join(work_days_values)
        
        # Get is_active
        is_active = request.form.get('is_active') == 'on'
        
        # Get notes
        notes = request.form.get('notes', '').strip() or None
        
        # If this is set as active, deactivate other active schedules for this employee
        if is_active:
            existing_active = WorkSchedule.query.filter_by(
                employee_id=employee_id,
                is_active=True
            ).all()
            
            for existing in existing_active:
                existing.is_active = False
        
        # Create work schedule entries for each selected shift type
        for shift_type in shift_types:
            if shift_type == 'regular':
                shift_start = datetime.strptime('08:00', '%H:%M').time()
                shift_end = datetime.strptime('17:00', '%H:%M').time()
            elif shift_type == 'overtime':
                shift_start = datetime.strptime('17:30', '%H:%M').time()
                shift_end = datetime.strptime('20:00', '%H:%M').time()
            else:
                continue
            
            schedule = WorkSchedule(
                employee_id=employee_id,
                shift_start=shift_start,
                shift_end=shift_end,
                effective_from=None,
                effective_to=None,
                work_days=work_days,
                is_active=is_active,
                notes=notes
            )
            
            db.session.add(schedule)
        
        db.session.commit()
        
        flash('Tạo lịch làm việc thành công', 'success')
        return redirect(url_for('admin.schedules'))
    
    # GET request
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    # Get employees who already have schedules
    employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
    employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
    
    return render_template('admin/schedule_form.html', 
                         schedule=None,
                         employees=employees,
                         employees_with_schedules=employee_ids_with_schedules)


@bp.route('/schedules/<int:schedule_id>/edit', methods=['GET', 'POST'])
@login_required
def schedule_edit(schedule_id: int):
    """Edit work schedule"""
    schedule = WorkSchedule.query.get_or_404(schedule_id)
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        if not employee_id:
            flash('Vui lòng chọn nhân viên', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=schedule,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        try:
            employee_id = int(employee_id)
        except (ValueError, TypeError):
            flash('Mã nhân viên không hợp lệ', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=schedule,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        # Get shift types
        shift_types = request.form.getlist('shift_types')
        
        # Ensure regular is always selected
        if 'regular' not in shift_types:
            shift_types.append('regular')
        
        # Remove duplicates
        shift_types = list(set(shift_types))
        
        if not shift_types:
            flash('Vui lòng chọn loại ca làm việc', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
            employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
            return render_template('admin/schedule_form.html', 
                                 schedule=schedule,
                                 employees=employees,
                                 employees_with_schedules=employee_ids_with_schedules)
        
        # Get work days
        work_days_list = request.form.getlist('work_days')
        required_days = ['0', '1', '2', '3', '4', '5']
        work_days_values = sorted(set(work_days_list + required_days), key=int)
        work_days = ','.join(work_days_values)
        
        # Get is_active
        is_active = request.form.get('is_active') == 'on'
        
        # Get notes
        notes = request.form.get('notes', '').strip() or None
        
        # Delete all existing active schedules for this employee (we'll create new ones)
        if is_active:
            existing_active = WorkSchedule.query.filter(
                WorkSchedule.employee_id == employee_id,
                WorkSchedule.is_active == True
            ).all()
            
            for existing in existing_active:
                db.session.delete(existing)
        
        # Create work schedule entries for each selected shift type
        for shift_type in shift_types:
            if shift_type == 'regular':
                shift_start = datetime.strptime('08:00', '%H:%M').time()
                shift_end = datetime.strptime('17:00', '%H:%M').time()
            elif shift_type == 'overtime':
                shift_start = datetime.strptime('17:30', '%H:%M').time()
                shift_end = datetime.strptime('20:00', '%H:%M').time()
            else:
                continue
            
            new_schedule = WorkSchedule(
                employee_id=employee_id,
                shift_start=shift_start,
                shift_end=shift_end,
                effective_from=None,
                effective_to=None,
                work_days=work_days,
                is_active=is_active,
                notes=notes
            )
            
            db.session.add(new_schedule)
        
        db.session.commit()
        
        flash('Cập nhật lịch làm việc thành công', 'success')
        return redirect(url_for('admin.schedules'))
    
    # GET request
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    # Get employees who already have schedules
    employees_with_schedules = db.session.query(WorkSchedule.employee_id).distinct().all()
    employee_ids_with_schedules = {row[0] for row in employees_with_schedules}
    
    return render_template('admin/schedule_form.html', 
                         schedule=schedule,
                         employees=employees,
                         employees_with_schedules=employee_ids_with_schedules)


@bp.route('/schedules/<int:schedule_id>/delete', methods=['POST'])
@login_required
def schedule_delete(schedule_id: int):
    """Delete work schedule"""
    schedule = WorkSchedule.query.get_or_404(schedule_id)
    employee_name = schedule.employee.name
    
    db.session.delete(schedule)
    db.session.commit()
    
    flash(f'Đã xóa lịch làm việc của {employee_name}', 'success')
    return redirect(url_for('admin.schedules'))


@bp.route('/attendance')
@login_required
def attendance():
    """Attendance records page"""
    today = date.today()
    
    # Get filter parameters
    filter_date = request.args.get('date')
    if filter_date:
        filter_date = _parse_date_string(filter_date)
        if not filter_date:
            filter_date = today
    else:
        filter_date = today
    
    employee_id_filter = request.args.get('employee_id', type=int)
    
    # Build query for existing records
    query = Attendance.query.filter_by(date=filter_date)
    
    if employee_id_filter:
        query = query.filter_by(employee_id=employee_id_filter)
    
    # Order by check-in time (most recent first), emulate NULLS LAST for MySQL/MariaDB
    # Put non-null check_in_time first, then sort by check_in_time descending
    records = query.order_by(Attendance.check_in_time.is_(None), Attendance.check_in_time.desc()).all()
    
    # Get all employees for filter dropdown
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()

    # Always synthesize "absent" records for employees without attendance
    # (we removed the status filter from the UI, so show combined view)
    employee_ids_with_records = {att.employee_id for att in records}

    # If an employee_id_filter is provided, limit the employees we check to that one
    if employee_id_filter:
        employees_to_check = [emp for emp in employees if emp.id == employee_id_filter]
    else:
        employees_to_check = employees

    # Create absent records for employees without attendance
    for emp in employees_to_check:
        if emp.id not in employee_ids_with_records:
            absent_att = Attendance(
                employee_id=emp.id,
                date=filter_date,
                status='absent'
            )
            absent_att.employee = emp  # Add employee relationship for template
            records.append(absent_att)

    # Re-sort after adding absent records
    records.sort(key=lambda x: (
        x.check_in_time is None,
        -x.check_in_time.timestamp() if x.check_in_time else 0
    ))
    
    return render_template('admin/attendance.html', 
                         records=records,
                         employees=employees,
                         today=filter_date)


@bp.route('/attendance/new', methods=['GET', 'POST'])
@login_required
def attendance_new():
    """Create new attendance record"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        if not employee_id:
            flash('Vui lòng chọn nhân viên', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 employees=employees,
                                 today=date.today())
        
        try:
            employee_id = int(employee_id)
        except (ValueError, TypeError):
            flash('Mã nhân viên không hợp lệ', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 employees=employees,
                                 today=date.today())
        
        # Get date
        date_str = request.form.get('date', '').strip()
        if not date_str:
            flash('Vui lòng chọn ngày', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 employees=employees,
                                 today=date.today())
        
        record_date = _parse_date_string(date_str)
        if not record_date:
            flash('Ngày không hợp lệ', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 employees=employees,
                                 today=date.today())
        
        # Verify employee exists
        employee = Employee.query.get(employee_id)
        if not employee:
            flash('Nhân viên không tồn tại', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 employees=employees,
                                 today=date.today())

        # Check if attendance record already exists
        existing = Attendance.query.filter_by(
            employee_id=employee_id,
            date=record_date
        ).first()
        
        if existing:
            flash('Bản ghi chấm công cho nhân viên này trong ngày này đã tồn tại. Vui lòng sửa bản ghi hiện có.', 'warning')
            return redirect(url_for('admin.attendance_edit', attendance_id=existing.id))
        
        # Get check-in/out times (parse as local timezone)
        check_in_time = _parse_local_datetime(request.form.get('check_in_time'))
        check_out_time = _parse_local_datetime(request.form.get('check_out_time'))
        check_in_time_2 = _parse_local_datetime(request.form.get('check_in_time_2'))
        check_out_time_2 = _parse_local_datetime(request.form.get('check_out_time_2'))
        overtime_check_in_time = _parse_local_datetime(request.form.get('overtime_check_in_time'))
        overtime_check_out_time = _parse_local_datetime(request.form.get('overtime_check_out_time'))
        
        # Get status
        status = request.form.get('status', 'present').strip()
        
        # Get working hours
        working_hours = request.form.get('working_hours', '').strip()
        try:
            working_hours = float(working_hours) if working_hours else None
        except ValueError:
            working_hours = None
        
        # Get overtime hours
        overtime_hours = request.form.get('overtime_hours', '').strip()
        try:
            overtime_hours = float(overtime_hours) if overtime_hours else None
        except ValueError:
            overtime_hours = None
        
        # Get notes
        notes = request.form.get('notes', '').strip() or None
        
        # Create attendance record (attach employee relationship so update_status can access it)
        attendance = Attendance(
            employee=employee,
            employee_id=employee_id,
            date=record_date,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            check_in_time_2=check_in_time_2,
            check_out_time_2=check_out_time_2,
            overtime_check_in_time=overtime_check_in_time,
            overtime_check_out_time=overtime_check_out_time,
            status=status,
            working_hours=working_hours or 0.0,
            overtime_hours=overtime_hours or 0.0,
            notes=notes
        )
        
        # Auto-calculate whenever any punch is saved so the full day can be summed.
        if any([check_in_time, check_out_time, check_in_time_2, check_out_time_2, overtime_check_in_time, overtime_check_out_time]):
            attendance.calculate_working_hours()
        attendance.update_status()
        
        db.session.add(attendance)
        db.session.commit()
        
        flash('Tạo bản ghi chấm công thành công', 'success')
        return redirect(url_for('admin.attendance'))
    
    # GET request
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    return render_template('admin/attendance_form.html', 
                         employees=employees,
                         today=date.today())


@bp.route('/attendance/<int:attendance_id>/edit', methods=['GET', 'POST'])
@login_required
def attendance_edit(attendance_id: int):
    """Edit attendance record"""
    attendance = Attendance.query.get_or_404(attendance_id)
    
    if request.method == 'POST':
        # Get employee_id
        employee_id = request.form.get('employee_id')
        if not employee_id:
            flash('Vui lòng chọn nhân viên', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 attendance=attendance,
                                 employees=employees,
                                 today=date.today())
        
        try:
            employee_id = int(employee_id)
        except (ValueError, TypeError):
            flash('Mã nhân viên không hợp lệ', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 attendance=attendance,
                                 employees=employees,
                                 today=date.today())
        
        # Get date
        date_str = request.form.get('date', '').strip()
        if not date_str:
            flash('Vui lòng chọn ngày', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 attendance=attendance,
                                 employees=employees,
                                 today=date.today())
        
        record_date = _parse_date_string(date_str)
        if not record_date:
            flash('Ngày không hợp lệ', 'danger')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 attendance=attendance,
                                 employees=employees,
                                 today=date.today())
        
        # Check if another record exists with same employee and date
        existing = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date == record_date,
            Attendance.id != attendance_id
        ).first()
        
        if existing:
            flash('Bản ghi chấm công cho nhân viên này trong ngày này đã tồn tại', 'warning')
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            return render_template('admin/attendance_form.html', 
                                 attendance=attendance,
                                 employees=employees,
                                 today=date.today())
        
        # Get check-in/out times (parse as local timezone)
        check_in_time = _parse_local_datetime(request.form.get('check_in_time'))
        check_out_time = _parse_local_datetime(request.form.get('check_out_time'))
        check_in_time_2 = _parse_local_datetime(request.form.get('check_in_time_2'))
        check_out_time_2 = _parse_local_datetime(request.form.get('check_out_time_2'))
        overtime_check_in_time = _parse_local_datetime(request.form.get('overtime_check_in_time'))
        overtime_check_out_time = _parse_local_datetime(request.form.get('overtime_check_out_time'))
        
        # Get status
        status = request.form.get('status', 'present').strip()
        
        # Get working hours
        working_hours = request.form.get('working_hours', '').strip()
        try:
            working_hours = float(working_hours) if working_hours else None
        except ValueError:
            working_hours = None
        
        # Get overtime hours
        overtime_hours = request.form.get('overtime_hours', '').strip()
        try:
            overtime_hours = float(overtime_hours) if overtime_hours else None
        except ValueError:
            overtime_hours = None
        
        # Get notes
        notes = request.form.get('notes', '').strip() or None
        
        # Update attendance record
        attendance.employee_id = employee_id
        attendance.date = record_date
        attendance.check_in_time = check_in_time
        attendance.check_out_time = check_out_time
        attendance.check_in_time_2 = check_in_time_2
        attendance.check_out_time_2 = check_out_time_2
        attendance.overtime_check_in_time = overtime_check_in_time
        attendance.overtime_check_out_time = overtime_check_out_time
        attendance.status = status
        attendance.notes = notes
        
        # Auto-calculate whenever any punch is saved so the full day can be summed.
        if any([check_in_time, check_out_time, check_in_time_2, check_out_time_2]):
            attendance.calculate_working_hours()
        else:
            attendance.working_hours = working_hours or 0.0
            attendance.overtime_hours = overtime_hours or 0.0
        attendance.update_status()
        
        db.session.commit()
        
        flash('Cập nhật bản ghi chấm công thành công', 'success')
        return redirect(url_for('admin.attendance'))
    
    # GET request
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    return render_template('admin/attendance_form.html', 
                         attendance=attendance,
                         employees=employees,
                         today=date.today())


@bp.route('/attendance/<int:attendance_id>/delete', methods=['POST'])
@login_required
def attendance_delete(attendance_id: int):
    """Delete attendance record"""
    attendance = Attendance.query.get_or_404(attendance_id)
    db.session.delete(attendance)
    db.session.commit()
    flash('Xóa bản ghi chấm công thành công', 'success')
    return redirect(url_for('admin.attendance'))


@bp.route('/reports')
@login_required
def reports():
    """Reports page"""
    report_type = request.args.get('type', 'daily')
    report_date = request.args.get('date')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    from app.services.reports_service import ReportsService
    
    report_data = None
    if report_type == 'daily':
        if report_date:
            report_date = _parse_date_string(report_date)
        if not report_date:
            report_date = date.today()
        report_data = ReportsService.get_daily_report(report_date)
        report_data['date'] = report_date.strftime('%d/%m/%Y')
    elif report_type == 'weekly':
        if report_date:
            start_date = _parse_date_string(report_date)
        else:
            start_date = None
        report_data = ReportsService.get_weekly_report(start_date)
        if report_data.get('start_date'):
            try:
                report_data['start_date'] = datetime.strptime(report_data['start_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                pass
        if report_data.get('end_date'):
            try:
                report_data['end_date'] = datetime.strptime(report_data['end_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                pass
    elif report_type == 'monthly':
        report_data = ReportsService.get_monthly_report(year, month)
    
    return render_template('admin/reports.html',
                         report_type=report_type,
                         report_data=report_data,
                         date=date)


@bp.route('/reports/export')
@login_required
def export_report():
    """Export report to Excel"""
    from flask import send_file
    from app.services.reports_service import ReportsService
    from app.services.export_service import ExportService
    import io
    import csv
    
    report_type = request.args.get('type', 'daily')
    report_date = request.args.get('date')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    out_format = request.args.get('format', 'excel')
    
    # Get report data
    report_data = None
    if report_type == 'daily':
        if report_date:
            report_date = _parse_date_string(report_date)
        if not report_date:
            report_date = date.today()
        report_data = ReportsService.get_daily_report(report_date)
    elif report_type == 'weekly':
        if report_date:
            start_date = _parse_date_string(report_date)
        else:
            start_date = None
        report_data = ReportsService.get_weekly_report(start_date)
    elif report_type == 'monthly':
        report_data = ReportsService.get_monthly_report(year, month)
    
    # Export to Excel
    if out_format == 'csv':
        # Build CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == 'daily':
            # headers
            headers = ['Nhân viên', 'Mã NV', 'Check-in', 'Check-out', 'Giờ làm (h)', 'Có OT', 'OT scheduled start', 'OT scheduled end', 'OT check-in', 'OT check-out', 'OT hours', 'OT (công)', 'Tổng công (h)', 'Trạng thái']
            writer.writerow(headers)
            for att in report_data.get('attendances', []):
                name = att.get('employee_name', '')
                code = att.get('employee_code', '')
                ci = att.get('check_in_time')
                co = att.get('check_out_time')
                ci_short = (ci.split('T')[1][:5]) if ci else ''
                co_short = (co.split('T')[1][:5]) if co else ''
                working_hours = att.get('working_hours', 0) or 0
                ot_break = att.get('overtime_breakdown', {}) or {}
                has_ot = 'yes' if ot_break.get('approval') == 'approved' else 'no'
                # scheduled window (default)
                scheduled_start = '17:30'
                scheduled_end = '20:00'
                ot_ci = att.get('overtime_check_in_time')
                ot_co = att.get('overtime_check_out_time')
                ot_ci_short = (ot_ci.split('T')[1][:5]) if ot_ci else ''
                ot_co_short = (ot_co.split('T')[1][:5]) if ot_co else ''
                # overtime_actual_hours is raw hours (if available); overtime_hours is OT points (converted)
                ot_actual = att.get('overtime_actual_hours') or 0
                ot_points = att.get('overtime_hours', 0) or 0
                total = round((working_hours or 0) + ot_points, 2)

                row = [name, code, ci_short, co_short, f"{working_hours:.2f}", has_ot, scheduled_start, scheduled_end, ot_ci_short, ot_co_short, f"{ot_actual:.2f}", f"{ot_points:.2f}", f"{total:.2f}", att.get('status_label') or att.get('status')]
                writer.writerow(row)
        else:
            # For weekly/monthly, produce simple rows per day
            headers = ['Ngày', 'Có mặt', 'Đi muộn', 'Vắng mặt', 'Giờ làm (h)', 'Tổng OT (h)']
            writer.writerow(headers)
            if report_type == 'weekly':
                for day in report_data.get('daily_stats', []):
                    writer.writerow([day.get('date'), day.get('present'), day.get('late'), day.get('absent'), day.get('working_hours'), ''])
            else:
                for day in report_data.get('daily_stats', []):
                    writer.writerow([day.get('date'), day.get('present'), day.get('late'), day.get('absent'), '', ''])

        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)

        # Filename
        if report_type == 'daily':
            filename = f'bao_cao_ngay_{report_data.get("date", "")}.csv'
        elif report_type == 'weekly':
            filename = f'bao_cao_tuan_{report_data.get("start_date","")}_to_{report_data.get("end_date","")}.csv'
        else:
            filename = f'bao_cao_thang_{year}_{month:02d}.csv'

        return send_file(
            mem,
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=filename
        )

    # default: Excel
    excel_file = ExportService.export_to_excel(report_data, report_type)
    
    # Generate filename
    if report_type == 'daily':
        filename = f'bao_cao_ngay_{report_data["date"]}.xlsx'
    elif report_type == 'weekly':
        filename = f'bao_cao_tuan_{report_data["start_date"]}_to_{report_data["end_date"]}.xlsx'
    else:
        filename = f'bao_cao_thang_{year}_{month:02d}.xlsx'
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/migrate-face-encodings', methods=['GET', 'POST'])
@login_required
def migrate_face_encodings():
    """Migrate face encodings from legacy table to multi-embedding table"""
    from app.services.face_service import FaceService
    import logging
    
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        try:
            face_service = FaceService(db.session)
            
            # Get all employees with legacy face encodings
            employees = Employee.query.filter(
                Employee.face_encoding.isnot(None),
                Employee.is_active == True
            ).all()
            
            migrated_count = 0
            skipped_count = 0
            failed_count = 0
            
            for employee in employees:
                try:
                    # Get legacy encoding
                    encoding = employee.get_face_encoding()
                    
                    if encoding is None:
                        skipped_count += 1
                        continue
                    
                    # Check if already exists in multi-embedding table
                    from app.models.face_embedding import FaceEmbedding
                    existing = db.session.query(FaceEmbedding).filter_by(
                        employee_code=employee.employee_code
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        logger.info(f"Employee {employee.employee_code} already has multi-embeddings")
                        continue
                    
                    # Add to multi-embedding table
                    result = face_service.add_face_embedding(
                        employee_code=employee.employee_code,
                        embedding=encoding,
                        variant_type='default',
                        embedding_type='standard',
                        set_as_primary=True
                    )
                    
                    if result['success']:
                        migrated_count += 1
                        logger.info(f"Migrated face encoding for {employee.employee_code}")
                    else:
                        failed_count += 1
                        logger.warning(f"Failed to migrate {employee.employee_code}: {result['message']}")
                
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error migrating {employee.employee_code}: {str(e)}")
            
            flash(
                f'✓ Migration hoàn tất: {migrated_count} thành công, {skipped_count} bỏ qua, {failed_count} thất bại',
                'success' if failed_count == 0 else 'warning'
            )
            return redirect(url_for('admin.dashboard'))
        
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            flash(f'❌ Lỗi migration: {str(e)}', 'danger')
            return redirect(url_for('admin.dashboard'))
    
    # GET request - show confirmation page
    legacy_count = Employee.query.filter(
        Employee.face_encoding.isnot(None),
        Employee.is_active == True
    ).count()
    
    from app.models.face_embedding import FaceEmbedding
    multi_count = db.session.query(FaceEmbedding).count()
    
    return render_template('admin/migrate_faces.html',
                         legacy_count=legacy_count,
                         multi_count=multi_count)


## (Policies removed per rollback to pre-scheduling baseline)

