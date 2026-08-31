"""add agent tools

Revision ID: c4f8a2d16b09
Revises: 9b3d5e1c7a42
Create Date: 2026-08-31 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c4f8a2d16b09'
down_revision: Union[str, Sequence[str], None] = '9b3d5e1c7a42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('tools', postgresql.ARRAY(sa.String(length=64)), server_default='{}', nullable=False))


def downgrade() -> None:
    op.drop_column('agents', 'tools')
