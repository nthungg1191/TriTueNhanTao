#!/usr/bin/env python3
"""Test new attendance route logic with absent records."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models.attendance import Attendance
from app.models.employee import Employee
from datetime import date

app = create_app()

with app.app_context():
    # Simulate route logic
    today = date(2026, 5, 15)
    
    # Get existing records
    records = Attendance.query.filter_by(date=today).all()
    employees = Employee.query.filter_by(is_active=True).all()
    
    print(f'Existing records: {len(records)}')
    print(f'Active employees: {len(employees)}\n')
    
    # Simulate absent record creation
    employee_ids_with_records = {att.employee_id for att in records}
    
    for emp in employees:
        if emp.id not in employee_ids_with_records:
            absent_att = Attendance(
                employee_id=emp.id,
                date=today,
                status='absent'
            )
            absent_att.employee = emp
            records.append(absent_att)
            print(f'Added absent record for: {emp.name}')
    
    print(f'\nTotal records after adding absent: {len(records)}')
    print('\nVerifying methods work:')
    for rec in records:
        print(f'  {rec.employee.name}: status={rec.status}, shift_breakdown={rec.get_shift_breakdown()}')
