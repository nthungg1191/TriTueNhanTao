"""Attendance kiosk routes"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app import db
from app.models import Employee, Attendance
from datetime import datetime, date
import os
from app.utils.image_utils import ImageProcessor
from app.utils.timezone_utils import get_local_now

bp = Blueprint('kiosk', __name__, url_prefix='/kiosk')


def _assign_attendance_photo(attendance, action_type: str, punch_slot: int, saved_path: str):
    if action_type == 'check-in':
        if punch_slot == 1:
            attendance.check_in_photo = saved_path
        else:
            attendance.check_in_photo_2 = saved_path
    else:
        if punch_slot == 1:
            attendance.check_out_photo = saved_path
        else:
            attendance.check_out_photo_2 = saved_path


def _ensure_today_attendance(employee, today):
    attendance = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
    if not attendance:
        attendance = Attendance(employee_id=employee.id, date=today)
        db.session.add(attendance)
    return attendance


def _validate_schedule(employee, today):
    schedule = employee.get_current_schedule()
    if not schedule:
        return jsonify({
            'status': 'error',
            'message': 'Không thể chấm công. Nhân viên chưa có lịch làm việc đang hoạt động. Vui lòng liên hệ quản trị viên.'
        }), 403

    if not schedule.is_effective_on(today):
        return jsonify({
            'status': 'error',
            'message': f'Lịch làm việc không có hiệu lực vào ngày {today.strftime("%d/%m/%Y")}. Vui lòng liên hệ quản trị viên.'
        }), 403

    weekday = today.weekday()
    if not schedule.is_weekday_allowed(weekday):
        weekday_names = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
        return jsonify({
            'status': 'error',
            'message': f'Hôm nay là {weekday_names[weekday]}, không phải ngày làm việc theo lịch của bạn. Vui lòng liên hệ quản trị viên.'
        }), 403

    return schedule


def _next_punch_action(attendance):
    """Legacy strict sequential slot picker.

    Retained for callers that still want the order-based behaviour. The kiosk
    endpoints prefer :func:`_resolve_time_based_action`.
    """
    if attendance.check_in_time is None:
        return 'check-in'
    if attendance.check_out_time is None:
        return 'check-out'
    if attendance.check_in_time_2 is None:
        return 'check-in'
    if attendance.check_out_time_2 is None:
        return 'check-out'
    # If the regular 2x check-in/out slots are full, allow overtime punches
    # when an approved overtime request exists for this attendance date.
    try:
        approved_ot = attendance._get_approved_overtime_request()
    except Exception:
        approved_ot = None

    if approved_ot:
        if attendance.overtime_check_in_time is None:
            return 'overtime_check-in'
        if attendance.overtime_check_out_time is None:
            return 'overtime_check-out'

    return None


def _resolve_time_based_action(attendance, now):
    """Pick the punch action by mapping the wall-clock time to a slot.

    Hard caps by shift (no auto-created punches):
        - Morning shift ends at 12:00. check_out_1 is allowed any time after
          check_in_1 and is capped at 13:00. Scanning before 12:00 with an
          open morning shift records an early check-out.
        - Lunch window 12:00 - 13:00: if the morning shift is still open,
          record check_out_1; otherwise record check_in_2 (covers employees
          who already punched out for lunch or who missed the morning shift
          entirely).
        - After 13:00: the morning shift's check-out window is closed. An
          open morning shift (``check_in_time`` filled, ``check_out_time``
          empty) is treated as missed; the current scan becomes check_in_2
          and ``update_status()`` marks the morning as ``missing_check_out``.
          No back-dated check-out is written.
        - Afternoon check-out: any time after check_in_2 up to 20:00 (early
          or on-time). OT (after 20:00) is delegated to the OT picker.

    Returns either a tuple ``(action_type, slot)`` for the regular slots, an
    OT action string, or ``None`` to indicate the punch should be skipped.
    """
    morning_end = now.replace(hour=12, minute=0, second=0, microsecond=0)
    lunch_end = now.replace(hour=13, minute=0, second=0, microsecond=0)
    final_end = now.replace(hour=20, minute=0, second=0, microsecond=0)

    # --- Trước 12:00 ---
    if now < morning_end:
        # Chưa check-in sáng -> check-in sáng
        if attendance.check_in_time is None:
            return ('check-in', 1)
        # Đã check-in sáng nhưng quét sớm trước 12:00 -> cho check-out sớm
        if attendance.check_out_time is None:
            return ('check-out', 1)
        # Đã check-out sáng rồi mà quét tiếp trước 12:00 -> bỏ qua
        return None

    # --- 12:00 - 13:00 ---
    if now < lunch_end:
        # Ca sáng đang mở (có check-in, chưa check-out) -> ưu tiên check-out
        if (attendance.check_in_time is not None
                and attendance.check_out_time is None):
            return ('check-out', 1)
        # Đã check-out sáng rồi (hoặc không có check-in sáng) -> check-in chiều
        if attendance.check_in_time_2 is None:
            return ('check-in', 2)
        return None

    # --- Sau 13:00 ---
    # Ca sáng đã bỏ lỡ check-out (có check_in nhưng chưa check_out, đã quá 13:00)
    # -> không check-out ngược, lượt quét này xử lý như check-in chiều.
    # update_status() sẽ tự set missing_check_out cho ca sáng.
    if (attendance.check_in_time is not None
            and attendance.check_out_time is None):
        if attendance.check_in_time_2 is None:
            return ('check-in', 2)
        return None

    # Ca chiều: đã check-in chiều và còn trong khung được phép check-out
    # (13:00 - 20:00, bao gồm cả check-out sớm trước 17:00)
    if attendance.check_in_time_2 is not None:
        if attendance.check_out_time_2 is None and now <= final_end:
            return ('check-out', 2)

        # --- Khung chuyển tiếp 17:00 - 17:30 ---
        # Ca chiều đã đóng (check_out_time_2 đã có). Trong khung này, ưu tiên
        # xử lý OT dựa trên trạng thái hiện tại thay vì chỉ defer sang OT picker.
        # Sau 17:30: deleg hoàn toàn sang _resolve_overtime_action (caller).
        transition_start = now.replace(hour=17, minute=0, second=0, microsecond=0)
        transition_end   = now.replace(hour=17, minute=30, second=0, microsecond=0)

        if transition_start <= now < transition_end:
            # Rule 2 & 5: ca chiều đã đóng VA đã có OT check-in -> check-out OT
            if (attendance.overtime_check_in_time is not None
                    and attendance.overtime_check_out_time is None):
                return 'overtime_check-out'

            # Rule 3 & 4: ca chiều đã đóng, CHƯA có OT check-in
            if (attendance.overtime_check_in_time is None):
                approved_ot = None
                try:
                    approved_ot = attendance._get_approved_overtime_request()
                except Exception:
                    pass
                if approved_ot is not None:
                    # Rule 3: ưu tiên đóng ca chiều đã xong ở trên,
                    # đến đây = ca chiều đã đóng + chưa có OT check-in + có đăng ký
                    # -> check-in OT (cho phép check-in sớm 17:00-17:30)
                    return 'overtime_check-in'
                # Rule 4: không có đăng ký tăng ca -> không tạo bản ghi OT
                return None

        return None

    # Chưa có check-in nào nhưng quét sau 13:00 -> ghi check-in chiều
    if attendance.check_in_time_2 is None:
        return ('check-in', 2)

    # 17:00+ and beyond: defer to OT logic (handled by caller).
    return None


def _resolve_overtime_action(attendance):
    """Pick the OT slot if an approved overtime request exists."""
    try:
        approved_ot = attendance._get_approved_overtime_request()
    except Exception:
        approved_ot = None

    if not approved_ot:
        return None

    if attendance.overtime_check_in_time is None:
        return 'overtime_check-in'
    if attendance.overtime_check_out_time is None:
        return 'overtime_check-out'
    return None


def _pick_action_for_kiosk(attendance, now):
    """Time-based action picker for the kiosk endpoints.

    Combines :func:`_resolve_time_based_action` for the regular slots and
    :func:`_resolve_overtime_action` for the overtime slots. Falls back to
    None (skip silently) when no valid slot can be filled.
    """
    action = _resolve_time_based_action(attendance, now)
    if action is not None:
        return action
    return _resolve_overtime_action(attendance)


@bp.route('/attendance')
def attendance_only():
    """Dedicated page for attendance via face recognition only"""
    return render_template('kiosk/attendance.html')


@bp.route('/check-in', methods=['POST'])
def check_in():
    """Handle check-in using employee_code or employee_id"""
    payload = request.get_json(silent=True) or {}
    employee_code = payload.get('employee_code')
    photo_data = payload.get('photo_path')  # Can be base64 or file path

    if not employee_code:
        return jsonify({'status': 'error', 'message': 'employee_code is required'}), 400

    employee = Employee.query.filter_by(employee_code=employee_code, is_active=True).first()

    if not employee:
        return jsonify({
            'status': 'error',
            'message': 'Nhân viên chưa có mặt trong hệ thống. Vui lòng liên hệ quản trị viên.'
        }), 404

    today = date.today()
    schedule_validation = _validate_schedule(employee, today)
    if isinstance(schedule_validation, tuple):
        return schedule_validation

    attendance = _ensure_today_attendance(employee, today)

    attendance.employee = employee
    # Determine the correct action (regular or overtime) using time-based rules
    now = get_local_now()
    action_type = _pick_action_for_kiosk(attendance, now)
    if action_type is None:
        return jsonify({
            'status': 'success',
            'message': 'Ngoài khung giờ chấm công',
            'skipped': True,
        })
    explicit_slot = None
    if isinstance(action_type, tuple):
        explicit_slot = action_type[1]
        action_type = action_type[0]

    try:
        if action_type == 'check-in':
            if explicit_slot is not None:
                punch_slot = attendance.check_in(slot=explicit_slot)
            else:
                punch_slot = attendance.check_in()
        elif action_type == 'overtime_check-in':
            # record overtime check-in as the extra punch (slot 3)
            timestamp = get_local_now()
            attendance.overtime_check_in_time = timestamp
            punch_slot = 3
        else:
            return jsonify({'status': 'error', 'message': 'Hành động không hợp lệ cho check-in'}), 409
    except ValueError as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 409

    # Save photo if provided (base64 string)
    if photo_data and photo_data.startswith('data:image'):
        saved_path = _save_attendance_photo(photo_data, employee_code, today, 'check-in')
        if saved_path:
            # Associate photos only for normal slots; OT photos use the standard check-in/out photos
            _assign_attendance_photo(attendance, 'check-in', punch_slot if punch_slot in (1, 2) else 1, saved_path)

    db.session.commit()

    return jsonify({'status': 'success', 'message': f'Check-in lần {punch_slot} thành công', 'punch_slot': punch_slot, 'attendance': attendance.to_dict()})


@bp.route('/check-out', methods=['POST'])
def check_out():
    """Handle check-out using employee_code or employee_id"""
    payload = request.get_json(silent=True) or {}
    employee_code = payload.get('employee_code')
    photo_data = payload.get('photo_path')  # Can be base64 or file path

    if not employee_code:
        return jsonify({'status': 'error', 'message': 'employee_code is required'}), 400

    employee = Employee.query.filter_by(employee_code=employee_code, is_active=True).first()

    if not employee:
        return jsonify({
            'status': 'error',
            'message': 'Nhân viên chưa có mặt trong hệ thống. Vui lòng liên hệ quản trị viên.'
        }), 404

    today = date.today()
    schedule_validation = _validate_schedule(employee, today)
    if isinstance(schedule_validation, tuple):
        return schedule_validation

    attendance = _ensure_today_attendance(employee, today)

    attendance.employee = employee
    # Determine the correct action (regular or overtime) using time-based rules
    now = get_local_now()
    action_type = _pick_action_for_kiosk(attendance, now)
    if action_type is None:
        return jsonify({
            'status': 'success',
            'message': 'Ngoài khung giờ chấm công',
            'skipped': True,
        })
    explicit_slot = None
    if isinstance(action_type, tuple):
        explicit_slot = action_type[1]
        action_type = action_type[0]

    try:
        if action_type == 'check-out':
            if explicit_slot is not None:
                punch_slot = attendance.check_out(slot=explicit_slot)
            else:
                punch_slot = attendance.check_out()
        elif action_type == 'overtime_check-out':
            timestamp = get_local_now()
            attendance.overtime_check_out_time = timestamp
            punch_slot = 4
            # After OT punch, recalc hours
            try:
                attendance.calculate_working_hours()
                attendance.update_status()
            except Exception:
                db.session.rollback()
                raise
        else:
            return jsonify({'status': 'error', 'message': 'Hành động không hợp lệ cho check-out'}), 409
    except ValueError as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 409

    # Save photo if provided (base64 string)
    if photo_data and photo_data.startswith('data:image'):
        saved_path = _save_attendance_photo(photo_data, employee_code, today, 'check-out')
        if saved_path:
            _assign_attendance_photo(attendance, 'check-out', punch_slot if punch_slot in (1, 2) else 2, saved_path)

    db.session.commit()

    return jsonify({'status': 'success', 'message': f'Check-out lần {punch_slot} thành công', 'punch_slot': punch_slot, 'attendance': attendance.to_dict()})


@bp.route('/auto', methods=['POST'])
def auto_attendance():
    """
    Auto-detect and handle check-in or check-out based on the current wall-clock
    time and the day's existing punches.
    """
    payload = request.get_json(silent=True) or {}
    employee_code = payload.get('employee_code')
    photo_data = payload.get('photo_path')  # Can be base64 or file path

    if not employee_code:
        return jsonify({'status': 'error', 'message': 'employee_code is required'}), 400

    employee = Employee.query.filter_by(employee_code=employee_code, is_active=True).first()

    if not employee:
        return jsonify({
            'status': 'error',
            'message': 'Nhân viên chưa có mặt trong hệ thống. Vui lòng liên hệ quản trị viên.'
        }), 404

    today = date.today()
    schedule_validation = _validate_schedule(employee, today)
    if isinstance(schedule_validation, tuple):
        return schedule_validation

    attendance = _ensure_today_attendance(employee, today)

    now = get_local_now()
    action_type = _pick_action_for_kiosk(attendance, now)
    if action_type is None:
        return jsonify({
            'status': 'success',
            'message': 'Ngoài khung giờ chấm công',
            'skipped': True,
        })
    explicit_slot = None
    if isinstance(action_type, tuple):
        explicit_slot = action_type[1]
        action_type = action_type[0]

    attendance.employee = employee
    try:
        if action_type == 'check-in':
            if explicit_slot is not None:
                punch_slot = attendance.check_in(slot=explicit_slot)
            else:
                punch_slot = attendance.check_in()
        elif action_type == 'check-out':
            if explicit_slot is not None:
                punch_slot = attendance.check_out(slot=explicit_slot)
            else:
                punch_slot = attendance.check_out()
        elif action_type == 'overtime_check-in':
            attendance.overtime_check_in_time = get_local_now()
            punch_slot = 3
        elif action_type == 'overtime_check-out':
            attendance.overtime_check_out_time = get_local_now()
            punch_slot = 4
            try:
                attendance.calculate_working_hours()
                attendance.update_status()
            except Exception:
                db.session.rollback()
                raise
        else:
            return jsonify({'status': 'error', 'message': 'Hành động tự động không hợp lệ'}), 409
    except ValueError as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 409

    # Save photo if provided (base64 string)
    if photo_data and photo_data.startswith('data:image'):
        saved_path = _save_attendance_photo(photo_data, employee_code, today, action_type)
        if saved_path:
            _assign_attendance_photo(attendance, action_type, punch_slot, saved_path)

    db.session.commit()

    return jsonify({'status': 'success', 'message': f'{action_type.replace("-", " ").title()} lần {punch_slot} thành công', 'punch_slot': punch_slot, 'attendance': attendance.to_dict()})


def _save_attendance_photo(photo_data: str, employee_code: str, date_obj: date, photo_type: str) -> str:
    """
    Save attendance photo from base64 to file
    
    Args:
        photo_data: Base64 encoded image string (data:image/...)
        employee_code: Employee code
        date_obj: Date object
        photo_type: 'check-in' or 'check-out'
        
    Returns:
        Relative file path or None if failed
    """
    try:
        # Decode base64 to image
        image = ImageProcessor.decode_from_base64(photo_data)
        if image is None:
            return None
        
        # Get upload directory from config
        upload_dir = current_app.config.get('UPLOAD_PATH', 'app/static/uploads')
        attendance_dir = os.path.join(upload_dir, 'attendance')
        os.makedirs(attendance_dir, exist_ok=True)
        
        # Generate filename: employee_code_date_type_timestamp.jpg
        timestamp = get_local_now().strftime('%H%M%S')
        filename = f"{employee_code}_{date_obj.strftime('%Y%m%d')}_{photo_type}_{timestamp}.jpg"
        file_path = os.path.join(attendance_dir, filename)
        
        # Save image
        if ImageProcessor.save_image(image, file_path, quality=85):
            # Return relative path from static folder
            # Path will be: /static/uploads/attendance/filename.jpg
            relative_path = f"/static/uploads/attendance/{filename}"
            return relative_path
        else:
            return None
            
    except Exception as e:
        current_app.logger.error(f"Error saving attendance photo: {str(e)}")
        return None

