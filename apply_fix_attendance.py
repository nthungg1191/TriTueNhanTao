from sqlalchemy import create_engine, text

DB_URI = 'mysql+pymysql://root:@localhost:3306/attendance_dbx1'
ATTENDANCE_ID = 110

engine = create_engine(DB_URI)

try:
    with engine.begin() as conn:
        # Append note if existing notes present
        update_sql = text("""
            UPDATE attendance
            SET status = :status,
                notes = CONCAT(COALESCE(notes, ''), :note)
            WHERE id = :aid
        """)
        note = '\n[Manual correction] status changed to present on 2026-05-15 by admin script.'
        result = conn.execute(update_sql, {'status': 'present', 'note': note, 'aid': ATTENDANCE_ID})
        print(f'Updated rows: {result.rowcount}')
except Exception as e:
    print('Error applying fix:', type(e).__name__, e)
