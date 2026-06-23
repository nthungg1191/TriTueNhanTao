"""add attendance_correction_requests table

Revision ID: b3e1f0c9d2a5
Revises: a7f2c1d9b8e4
Create Date: 2026-06-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3e1f0c9d2a5'
down_revision = 'a7f2c1d9b8e4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('attendance_correction_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('reason_type', sa.String(length=30), nullable=False),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('check_out_time', sa.DateTime(), nullable=True),
        sa.Column('check_in_time_2', sa.DateTime(), nullable=True),
        sa.Column('check_out_time_2', sa.DateTime(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('admin_note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('attendance_correction_requests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_attendance_correction_requests_employee_id'), ['employee_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_attendance_correction_requests_reviewer_id'), ['reviewer_id'], unique=False)
        batch_op.create_index('idx_correction_employee_date', ['employee_id', 'date'], unique=False)


def downgrade():
    with op.batch_alter_table('attendance_correction_requests', schema=None) as batch_op:
        batch_op.drop_index('idx_correction_employee_date')
        batch_op.drop_index(batch_op.f('ix_attendance_correction_requests_reviewer_id'))
        batch_op.drop_index(batch_op.f('ix_attendance_correction_requests_employee_id'))

    op.drop_table('attendance_correction_requests')