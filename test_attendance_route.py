#!/usr/bin/env python3
"""Test the attendance route with mock Flask context."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models.attendance import Attendance
from app.models.employee import Employee
from datetime import date

app = create_app()

try:
    with app.test_client() as client:
        with app.test_request_context('/admin/attendance'):
            from flask import request
            from app.routes.admin import _parse_date_string
            
            print('Testing attendance route logic...')
            
            today = date.today()
            filter_date = today
            status_filter = None
            employee_id_filter = None
            
            # Build query for existing records
            query = Attendance.query.filter_by(date=filter_date)
            
            if status_filter:
                query = query.filter_by(status=status_filter)
            
            if employee_id_filter:
                query = query.filter_by(employee_id=employee_id_filter)
            
            records = query.order_by(Attendance.check_in_time.is_(None), Attendance.check_in_time.desc()).all()
            
            # Get all employees for filter dropdown
            employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
            
            # Add absent records for employees who didn't check in
            if not status_filter and not employee_id_filter:
                employee_ids_with_records = {att.employee_id for att in records}
                
                for emp in employees:
                    if emp.id not in employee_ids_with_records:
                        absent_att = Attendance(
                            employee_id=emp.id,
                            date=filter_date,
                            status='absent'
                        )
                        absent_att.employee = emp
                        records.append(absent_att)
                        print(f'Added: {emp.name}')
                
                # Re-sort after adding absent records
                records.sort(key=lambda x: (
                    x.check_in_time is None,
                    -x.check_in_time.timestamp() if x.check_in_time else 0
                ))
            
            print(f'Total records: {len(records)}')
            for r in records:
                print(f'  {r.employee.name}: id={r.id}, status={r.status}, check_in={r.check_in_time}')
            
            print('\nRoute logic OK!')
            
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
