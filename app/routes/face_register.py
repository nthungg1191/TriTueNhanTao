"""Legacy face registration routes (kept for backward compatibility)."""
from flask import Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Employee, User
from app.services.face_service import FaceService
import base64
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os

bp = Blueprint('face_register', __name__, url_prefix='/admin/face-register')

MAX_REGISTER_IMAGE_WIDTH = 640
MAX_REGISTER_IMAGE_HEIGHT = 640


def resize_for_face_registration(image):
    """Resize large images before face detection to speed up registration."""
    height, width = image.shape[:2]
    if width <= MAX_REGISTER_IMAGE_WIDTH and height <= MAX_REGISTER_IMAGE_HEIGHT:
        return image

    scale = min(MAX_REGISTER_IMAGE_WIDTH / width, MAX_REGISTER_IMAGE_HEIGHT / height)
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bạn không có quyền truy cập', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@admin_required
def index():
    """Redirect old face registration page to employee management workflow."""
    flash('Đã chuyển sang luồng mới: tải ảnh ngay trong mục Nhân viên để tự động nhận diện.', 'info')
    return redirect(url_for('admin.employees'))


@bp.route('/upload/<int:employee_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_face(employee_id):
    """Redirect old upload route to employee edit page."""
    Employee.query.get_or_404(employee_id)
    flash('Trang này đã ngừng dùng. Vui lòng tải ảnh trong form Sửa nhân viên.', 'info')
    return redirect(url_for('admin.employee_edit', employee_id=employee_id))


@bp.route('/api/upload-base64/<int:employee_id>', methods=['POST'])
@login_required
@admin_required
def upload_face_base64(employee_id):
    """Legacy API endpoint removed in favor of employee photo workflow."""
    Employee.query.get_or_404(employee_id)
    return jsonify({
        'success': False,
        'message': 'Endpoint cũ đã ngừng dùng. Vui lòng cập nhật ảnh trong mục Nhân viên để tự động tạo nhận diện.'
    }), 410


@bp.route('/delete/<int:employee_id>', methods=['POST'])
@login_required
@admin_required
def delete_face(employee_id):
    """Delete face encoding for an employee"""
    employee = Employee.query.get_or_404(employee_id)
    
    try:
        face_service = FaceService(db.session)
        
        # Delete from legacy table
        result = face_service.delete_employee_face(employee.employee_code)
        
        # Delete from multi-embedding table
        embedding_result = face_service.delete_all_employee_embeddings(employee.employee_code)
        
        if result['success'] or embedding_result['success']:
            flash(f'✓ Đã xóa khuôn mặt của {employee.name}', 'success')
        else:
            flash(f'❌ Lỗi xóa khuôn mặt', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Lỗi: {str(e)}', 'danger')
    
    return redirect(url_for('face_register.index'))
