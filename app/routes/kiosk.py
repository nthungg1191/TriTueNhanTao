"""Attendance kiosk routes"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app import db
from app.models import Employee, Attendance
from datetime import datetime, date
import os
from app.utils.image_utils import ImageProcessor

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
    # Determine the correct action (normal or overtime) based on current state
    action_type = _next_punch_action(attendance)
    if action_type is None:
        return jsonify({'status': 'error', 'message': 'Đã đủ 2 lần check-in và 2 lần check-out trong ngày'}), 409

    try:
        if action_type == 'check-in':
            punch_slot = attendance.check_in()
        elif action_type == 'overtime_check-in':
            # record overtime check-in as the extra punch (slot 3)
            timestamp = datetime.now()
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
    # Determine the correct action (normal or overtime) based on current state
    action_type = _next_punch_action(attendance)
    if action_type is None:
        return jsonify({'status': 'error', 'message': 'Đã đủ 2 lần check-in và 2 lần check-out trong ngày'}), 409

    try:
        if action_type == 'check-out':
            punch_slot = attendance.check_out()
        elif action_type == 'overtime_check-out':
            timestamp = datetime.now()
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
    Auto-detect and handle check-in or check-out based on current status.
    If employee hasn't checked in today, do check-in.
    If employee has checked in, do check-out.
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

    action_type = _next_punch_action(attendance)
    if action_type is None:
        return jsonify({'status': 'error', 'message': 'Đã đủ 2 lần check-in và 2 lần check-out trong ngày'}), 409

    attendance.employee = employee
    try:
        if action_type == 'check-in':
            punch_slot = attendance.check_in()
        elif action_type == 'check-out':
            punch_slot = attendance.check_out()
        elif action_type == 'overtime_check-in':
            attendance.overtime_check_in_time = datetime.now()
            punch_slot = 3
        elif action_type == 'overtime_check-out':
            attendance.overtime_check_out_time = datetime.now()
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
        timestamp = datetime.now().strftime('%H%M%S')
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

