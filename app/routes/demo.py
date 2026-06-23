"""Demo routes for face recognition"""
from flask import Blueprint, current_app, render_template, jsonify
from app.models import Employee

bp = Blueprint('demo', __name__, url_prefix='/demo')


@bp.route('/face-recognition')
@bp.route('/face_recognition')
@bp.route('/face_recognition.html')
def face_recognition():
    """Demo page for face recognition"""
    return render_template('demo/face_recognition.html')


@bp.route('/employee/<employee_code>', methods=['GET'])
def get_employee_info(employee_code):
    """Get employee information by employee_code (for demo purposes, no login required)"""
    try:
        employee = Employee.query.filter_by(employee_code=employee_code, is_active=True).first()
        
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Employee not found'
            }), 404
        
        return jsonify({
            'success': True,
            'employee': {
                'employee_code': employee.employee_code,
                'name': employee.name,
                'email': employee.email,
                'phone': employee.phone,
                'department': employee.get_department_name(),  
                'department_code': employee.get_department_code(),  # NEW
                'position': employee.position,
                'photo_path': employee.photo_path,
                'hire_date': employee.hire_date.isoformat() if employee.hire_date else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Error loading demo employee info for %s", employee_code)
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

