"""update_call_logs_fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('call_logs', sa.Column('assistant_name', sa.String(100), nullable=True))
    op.add_column('call_logs', sa.Column('assistant_phone_number', sa.String(30), nullable=True))
    op.add_column('call_logs', sa.Column('customer_phone_number', sa.String(30), nullable=True))
    op.add_column('call_logs', sa.Column('call_type', sa.String(30), nullable=True))
    op.add_column('call_logs', sa.Column('ended_reason', sa.String(100), nullable=True))
    op.add_column('call_logs', sa.Column('success_evaluation', sa.String(50), nullable=True))
    op.add_column('call_logs', sa.Column('score', sa.Float(), nullable=True))

    # Migrate old phone → customer_phone_number
    op.execute("UPDATE call_logs SET customer_phone_number = phone WHERE customer_phone_number IS NULL")

    op.drop_column('call_logs', 'phone')
    op.drop_column('call_logs', 'end_time')
    op.drop_column('call_logs', 'outcome')
    op.execute("DROP TYPE IF EXISTS calloutcome")


def downgrade() -> None:
    op.add_column('call_logs', sa.Column('phone', sa.String(20), nullable=False, server_default='unknown'))
    op.add_column('call_logs', sa.Column('end_time', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('call_logs', 'score')
    op.drop_column('call_logs', 'success_evaluation')
    op.drop_column('call_logs', 'ended_reason')
    op.drop_column('call_logs', 'call_type')
    op.drop_column('call_logs', 'customer_phone_number')
    op.drop_column('call_logs', 'assistant_phone_number')
    op.drop_column('call_logs', 'assistant_name')
