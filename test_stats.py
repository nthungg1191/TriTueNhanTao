#!/usr/bin/env python3
"""Check what stats will display after route change."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models.attendance import Attendance
from app.models.employee import Employee
from datetime import date

app = create_app()

with app.app_context():
    today = date(2026, 5, 15)
    
    # Simulate route logic
    records = Attendance.query.filter_by(date=today).all()
    employees = Employee.query.filter_by(is_active=True).all()
    
    # Add absent records
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
    
    # Calculate stats like template does
    total = len(records)
    present = sum(1 for r in records if r.status == 'present')
    late = sum(1 for r in records if r.status == 'late')
    absent = sum(1 for r in records if r.status == 'absent')
    early_leave = sum(1 for r in records if r.status == 'early_leave')
    missing_check_in = sum(1 for r in records if r.status == 'missing_check_in')
    missing_check_out = sum(1 for r in records if r.status == 'missing_check_out')
    
    print('Stats after route change:')
    print(f'  Tổng số: {total}')
    print(f'  Có mặt: {present}')
    print(f'  Đi muộn: {late}')
    print(f'  Vắng mặt: {absent}')
    print(f'  Nghỉ sớm: {early_leave}')
    print(f'  Thiếu check-in: {missing_check_in}')
    print(f'  Thiếu check-out: {missing_check_out}')
