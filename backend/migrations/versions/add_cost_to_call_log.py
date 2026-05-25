"""
Add cost field to call_logs
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('call_logs', sa.Column('cost', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('call_logs', 'cost')
