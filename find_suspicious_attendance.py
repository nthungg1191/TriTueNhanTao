from sqlalchemy import create_engine, text
from datetime import date, timedelta

DB_URI = 'mysql+pymysql://root:@localhost:3306/attendance_dbx1'
DAYS = 7

engine = create_engine(DB_URI)

target_from = (date.today() - timedelta(days=DAYS)).isoformat()

def fmt_td(td):
    if td is None:
        return None
    # td may be stored as time delta in some DBs; try to format
    try:
        # If it's timedelta
        s = (date.min + td).time().isoformat()
        return s
    except Exception:
        return str(td)

try:
    with engine.connect() as conn:
        q = text("""
        SELECT a.id, a.employee_id, a.date, a.status, a.check_in_time, a.check_out_time,
               ws.id AS ws_id, ws.shift_start, ws.shift_end
        FROM attendance a
        LEFT JOIN work_schedules ws ON ws.employee_id = a.employee_id AND ws.is_active = 1
        WHERE a.date >= :from_date AND a.status = 'late'
        ORDER BY a.date DESC
        """)
        rows = conn.execute(q, {'from_date': target_from}).fetchall()
        print(f"Late records since {target_from}: {len(rows)}\n")
        for r in rows:
            m = dict(r._mapping)
            print(f"id={m['id']} emp={m['employee_id']} date={m['date']} status={m['status']}")
            print(f"  check_in={m['check_in_time']} check_out={m['check_out_time']}")
            print(f"  schedule id={m['ws_id']} start={fmt_td(m['shift_start'])} end={fmt_td(m['shift_end'])}\n")
except Exception as e:
    print('Error querying DB:', type(e).__name__, e)
