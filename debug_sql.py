from sqlalchemy import create_engine, text
from datetime import date

# Change URI if necessary
DB_URI = 'mysql+pymysql://root:@localhost:3306/attendance_dbx1'
TARGET_DATE = '2026-05-15'

engine = create_engine(DB_URI)

try:
    with engine.connect() as conn:
        query = text("SELECT id, employee_id, status, check_in_time, check_out_time, check_in_time_2, check_out_time_2 FROM attendance WHERE date = :d")
        result = conn.execute(query, {'d': TARGET_DATE})
        rows = result.fetchall()
        print(f"Found {len(rows)} attendance rows for {TARGET_DATE}")
        counts = {}
        for r in rows:
            d = dict(r._mapping)
            print(d)
            counts[d.get('status')] = counts.get(d.get('status'), 0) + 1
        print('\nStatus counts:')
        for k, v in counts.items():
            print(f"  {k}: {v}")
except Exception as e:
    print('Error querying DB:', type(e).__name__, e)

# Also inspect work schedule for the affected employee (if any)
try:
    with engine.connect() as conn:
        sched_q = text("SELECT id, employee_id, shift_start, shift_end, is_active FROM work_schedules WHERE employee_id = :eid AND is_active = 1 LIMIT 1")
        sched_res = conn.execute(sched_q, {'eid': 21}).fetchone()
        print('\nActive schedule for employee 21:')
        if sched_res:
            print(dict(sched_res._mapping))
        else:
            print('  No active schedule found')
except Exception as e:
    print('Error querying schedules:', type(e).__name__, e)
