#!/usr/bin/env python3
"""Check all employees attendance status."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models.employee import Employee
from app.models.attendance import Attendance
from datetime import date

app = create_app()
with app.app_context():
    # Get all active employees
    employees = Employee.query.filter_by(is_active=True).all()
    print(f'Total active employees: {len(employees)}\n')
    
    # Check attendance for today
    today = date(2026, 5, 15)
    has_record = []
    no_record = []
    
    for emp in employees:
        att = Attendance.query.filter_by(employee_id=emp.id, date=today).first()
        if att:
            has_record.append(f'{emp.name} (ID {emp.id}): {att.status}')
        else:
            no_record.append(f'{emp.name} (ID {emp.id}): NO RECORD')
    
    print('=== With Attendance Records ===')
    for line in has_record:
        print(line)
    
    print(f'\n=== Without Attendance Records ===')
    for line in no_record:
        print(line)
    
    print(f'\nSummary: {len(has_record)} with records, {len(no_record)} without records')
