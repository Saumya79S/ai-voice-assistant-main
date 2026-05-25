"""add_missing_tables

Revision ID: a1b2c3d4e5f6
Revises: ecf8ef0c37b0
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ecf8ef0c37b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'availability_rules' not in existing_tables:
        op.create_table(
            'availability_rules',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('day_of_week', sa.SmallInteger(), nullable=False),
            sa.Column('start_time', sa.Time(), nullable=False),
            sa.Column('end_time', sa.Time(), nullable=False),
            sa.Column('slot_duration', sa.Integer(), default=30),
            sa.Column('is_active', sa.Boolean(), default=True),
        )

    if 'appointments' not in existing_tables:
        op.create_table(
            'appointments',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('phone', sa.String(20), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('start_time', sa.Time(), nullable=False),
            sa.Column('end_time', sa.Time(), nullable=False),
            sa.Column('status', sa.Enum('pending', 'confirmed', 'cancelled', 'completed', name='appointmentstatus'), default='confirmed'),
            sa.Column('notes', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )

    if 'call_logs' not in existing_tables:
        op.create_table(
            'call_logs',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('phone', sa.String(20), nullable=False),
            sa.Column('vapi_call_id', sa.String(100), nullable=True, unique=True),
            sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('duration_seconds', sa.Float(), nullable=True),
            sa.Column('outcome', sa.Enum('booked', 'failed', 'transferred', 'abandoned', name='calloutcome'), default='abandoned'),
            sa.Column('transcript', sa.String(10000), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )

    if 'agents' not in existing_tables:
        op.create_table(
            'agents',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('prompt', sa.Text(), nullable=False),
            sa.Column('voice', sa.String(50), default='jennifer-playht'),
            sa.Column('vapi_assistant_id', sa.String(100), nullable=True),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'agents' in existing_tables:
        op.drop_table('agents')
    if 'call_logs' in existing_tables:
        op.drop_table('call_logs')
    if 'appointments' in existing_tables:
        op.drop_table('appointments')
    if 'availability_rules' in existing_tables:
        op.drop_table('availability_rules')
    op.execute('DROP TYPE IF EXISTS calloutcome')
    op.execute('DROP TYPE IF EXISTS appointmentstatus')
