"""Authentication routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, SystemLog

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page only."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản đã bị vô hiệu hóa.', 'danger')
                return render_template('auth/login.html')

            if getattr(user, 'role', None) != 'admin':
                flash('Chỉ quản trị viên được đăng nhập. Nhân viên hãy dùng nút chấm công riêng.', 'info')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            # Log action
            SystemLog.log_action(
                user_id=user.id,
                action='login',
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            return redirect(url_for('admin.dashboard'))
        else:
            if user:
                user.increment_failed_login()
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    """Employee login page."""
    if current_user.is_authenticated:
        return redirect(url_for('employee.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Tài khoản chưa được tạo. Vui lòng liên hệ quản trị viên để được cấp tài khoản.', 'warning')
            return render_template('auth/employee_login.html')

        if user.check_password(password):
            if not user.is_active:
                flash('Tài khoản đã bị vô hiệu hóa.', 'danger')
                return render_template('auth/employee_login.html')

            if getattr(user, 'role', None) != 'employee':
                flash('Chỉ nhân viên mới được đăng nhập ở trang này.', 'info')
                return render_template('auth/employee_login.html')

            login_user(user, remember=remember)
            user.update_last_login()

            SystemLog.log_action(
                user_id=user.id,
                action='login',
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )

            return redirect(url_for('employee.dashboard'))
        else:
            # Incorrect password for existing user
            user.increment_failed_login()
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')

    return render_template('auth/employee_login.html')


@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    SystemLog.log_action(
        user_id=current_user.id,
        action='logout',
        ip_address=request.remote_addr
    )
    logout_user()
    flash('Đã đăng xuất thành công.', 'success')
    return redirect(url_for('auth.login'))

