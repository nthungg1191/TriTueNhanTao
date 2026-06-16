from sqlalchemy import create_engine, text
from datetime import date, timedelta
import csv

DB_URI = 'mysql+pymysql://root:@localhost:3306/attendance_dbx1'
DAYS = 30
OUT_PATH = 'late_report.csv'

engine = create_engine(DB_URI)

try:
    with engine.connect() as conn:
        q = text("""
        SELECT a.id, a.employee_id, a.date, a.status, a.check_in_time, a.check_out_time, a.check_in_time_2, a.check_out_time_2, a.notes,
               ws.id AS ws_id, ws.shift_start, ws.shift_end
        FROM attendance a
        LEFT JOIN work_schedules ws ON ws.employee_id = a.employee_id AND ws.is_active = 1
        WHERE a.date >= :from_date AND a.status = 'late'
        ORDER BY a.date DESC
        """)
        from_date = (date.today() - timedelta(days=DAYS)).isoformat()
        rows = conn.execute(q, {'from_date': from_date}).fetchall()
        print(f'Found {len(rows)} late records since {from_date}')

        with open(OUT_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id','employee_id','date','status','check_in_time','check_out_time','check_in_time_2','check_out_time_2','notes','schedule_id','shift_start','shift_end'])
            for r in rows:
                m = dict(r._mapping)
                writer.writerow([
                    m.get('id'), m.get('employee_id'), m.get('date'), m.get('status'),
                    m.get('check_in_time'), m.get('check_out_time'), m.get('check_in_time_2'), m.get('check_out_time_2'),
                    (m.get('notes') or '').replace('\n',' | '), m.get('ws_id'), m.get('shift_start'), m.get('shift_end')
                ])
        print('CSV written to', OUT_PATH)
except Exception as e:
    print('Error:', type(e).__name__, e)
