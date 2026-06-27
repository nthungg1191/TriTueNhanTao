"""add is_late_minutes to attendance

Revision ID: c4d5e6f7a8b9
Revises: b3e1f0c9d2a5
Create Date: 2026-06-27 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4d5e6f7a8b9'
down_revision = 'b3e1f0c9d2a5'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Thêm cột is_late_minutes
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_late_minutes', sa.Integer(), nullable=False, server_default='0')
        )

    # 2) Tính lại is_late_minutes cho các bản ghi đang có status='late'
    #    dựa trên check_in_time so với 08:00 và check_in_time_2 so với 13:00.
    from datetime import datetime, time as dt_time

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT id, date, check_in_time, check_in_time_2 "
            "FROM attendance WHERE status = 'late'"
        )
    ).fetchall()

    for att_id, att_date, ci, ci2 in rows:
        late_minutes = 0
        if ci is not None and att_date is not None:
            morning_deadline = datetime.combine(att_date, dt_time(8, 0))
            if ci > morning_deadline:
                late_minutes += int((ci - morning_deadline).total_seconds() // 60)
        if ci2 is not None and att_date is not None:
            lunch_return = datetime.combine(att_date, dt_time(13, 0))
            if ci2 > lunch_return:
                late_minutes += int((ci2 - lunch_return).total_seconds() // 60)
        conn.execute(
            sa.text("UPDATE attendance SET is_late_minutes = :m WHERE id = :i"),
            {"m": late_min, "i": att_id}
        )

    # 3) Đổi status='late' -> 'present' cho bản ghi đủ 4 mốc chấm công
    conn.execute(
        sa.text(
            "UPDATE attendance SET status = 'present' "
            "WHERE status = 'late' "
            "AND check_in_time IS NOT NULL AND check_out_time IS NOT NULL "
            "AND check_in_time_2 IS NOT NULL AND check_out_time_2 IS NOT NULL"
        )
    )


def downgrade():
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.drop_column('is_late_minutes')