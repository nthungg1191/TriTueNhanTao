#!/usr/bin/env python3
"""Debug attendance records."""
from app import create_app, db
from app.models.attendance import Attendance
from app.models.employee import Employee
from datetime import date

app = create_app()
with app.app_context():
    # Get all attendance records for today
    today = date(2026, 5, 15)
    records = Attendance.query.filter_by(date=today).all()
    
    print(f'=== Attendance Records for {today} ===')
    print(f'Total records: {len(records)}\n')
    
    status_counts = {}
    for att in records:
        emp = Employee.query.get(att.employee_id)
        print(f'Employee: {emp.name if emp else "N/A"} (ID: {att.employee_id})')
        print(f'  Status: {att.status}')
        print(f'  Check-in 1: {att.check_in_time}')
        print(f'  Check-out 1: {att.check_out_time}')
        print(f'  Check-in 2: {att.check_in_time_2}')
        print(f'  Check-out 2: {att.check_out_time_2}')
        print(f'  Working hours: {att.working_hours}')
        print()
        
        status_counts[att.status] = status_counts.get(att.status, 0) + 1
    
    print('=== Status Summary ===')
    for status, count in sorted(status_counts.items()):
        print(f'{status}: {count}')
