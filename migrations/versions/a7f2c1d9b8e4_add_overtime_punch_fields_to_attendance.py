"""add overtime punch fields to attendance

Revision ID: a7f2c1d9b8e4
Revises: 46e38e9d84d5
Create Date: 2026-05-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7f2c1d9b8e4'
down_revision = '46e38e9d84d5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('overtime_check_in_time', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('overtime_check_out_time', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.drop_column('overtime_check_out_time')
        batch_op.drop_column('overtime_check_in_time')
