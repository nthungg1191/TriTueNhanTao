import json
from app import create_app, db
from app.models import Attendance
from sqlalchemy import inspect

app = create_app()
ctx = app.app_context()
ctx.push()
try:
    cols = inspect(db.engine).get_columns('attendance')
    print('COLUMNS:')
    print(json.dumps([c['name'] for c in cols], ensure_ascii=False))

    rows = Attendance.query.filter(
        (Attendance.overtime_check_in_time != None) | (Attendance.overtime_check_out_time != None)
    ).order_by(Attendance.date.desc()).limit(50).all()

    out = []
    for r in rows:
        out.append({
            'id': r.id,
            'employee_id': r.employee_id,
            'employee_name': r.employee.name if getattr(r, 'employee', None) else None,
            'date': str(r.date),
            'overtime_check_in_time': str(r.overtime_check_in_time),
            'overtime_check_out_time': str(r.overtime_check_out_time),
            'working_hours': r.working_hours,
            'overtime_hours': r.overtime_hours,
        })

    print('ROWS:')
    print(json.dumps(out, ensure_ascii=False, indent=2))
finally:
    ctx.pop()
