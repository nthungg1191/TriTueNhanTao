
import os
import socket
import threading
import webbrowser
from flask import redirect, url_for
from app import create_app, db
from app.models import User, Employee, Attendance, SystemLog

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)


def open_start_page(port):
    """Open the login page after the server starts."""
    webbrowser.open_new(f'http://127.0.0.1:{port}/auth/login')


def is_port_free(port):
    """Check whether a TCP port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False


@app.route('/')
def index():
    """Redirect to the admin login page when the app starts."""
    return redirect(url_for('auth.login'))

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Employee': Employee,
        'Attendance': Attendance,
        'SystemLog': SystemLog
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('✅ Database tables created successfully!')


@app.cli.command()
def drop_db():
    """Drop all database tables"""
    if input('Are you sure you want to drop all tables? (yes/no): ').lower() == 'yes':
        db.drop_all()
        print('✅ All tables dropped!')
    else:
        print('❌ Operation cancelled')


@app.cli.command()
def seed_db():
    """Seed database with initial data"""
    from werkzeug.security import generate_password_hash
    from datetime import date, time
    
    print('🌱 Seeding database...')
    
    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@attendance.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print('✅ Created admin user (username: admin, password: admin123)')
    
    # Create sample employees
    sample_employees = [
        {
            'employee_code': 'EMP001',
            'name': 'Nguyễn Văn A',
            'email': 'nguyenvana@company.com',
            'phone': '0901234567',
            'department': 'Sản xuất',
            'position': 'Công nhân',
            'hire_date': date(2024, 1, 15)
        },
        {
            'employee_code': 'EMP002',
            'name': 'Trần Thị B',
            'email': 'tranthib@company.com',
            'phone': '0902345678',
            'department': 'Sản xuất',
            'position': 'Công nhân',
            'hire_date': date(2024, 2, 1)
        },
        {
            'employee_code': 'EMP003',
            'name': 'Lê Văn C',
            'email': 'levanc@company.com',
            'phone': '0903456789',
            'department': 'Kỹ thuật',
            'position': 'Kỹ thuật viên',
            'hire_date': date(2024, 1, 20)
        }
    ]
    
    # Create Employee and User records for sample employees
    for emp in sample_employees:
        existing_emp = Employee.query.filter_by(employee_code=emp['employee_code']).first()
        if not existing_emp:
            new_emp = Employee(
                employee_code=emp['employee_code'],
                name=emp['name'],
                email=emp.get('email'),
                phone=emp.get('phone'),
                department=emp.get('department'),
                position=emp.get('position'),
                hire_date=emp.get('hire_date'),
                is_active=True
            )
            db.session.add(new_emp)

            # Create a corresponding User account (username = employee_code)
            existing_user = User.query.filter_by(username=emp['employee_code']).first()
            if not existing_user:
                u = User(
                    username=emp['employee_code'],
                    email=emp.get('email') or f"{emp['employee_code'].lower()}@example.com",
                    role='employee',
                    is_active=True
                )
                # default password: employee_code lowercased
                u.set_password(emp['employee_code'].lower())
                db.session.add(u)

    db.session.commit()
    print('🎉 Database seeded successfully!')


def start_server(port, debug_mode=False):
    print(f'Starting server on port {port}...')
    threading.Timer(1.0, lambda: open_start_page(port)).start()
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', '5555'))
    selected_port = port

    while not is_port_free(selected_port):
        print(f'Port {selected_port} is busy, trying {selected_port + 1} instead.')
        selected_port += 1

    start_server(selected_port, debug_mode=debug_mode)

