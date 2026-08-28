"""add providers api keys agents and user plan

Revision ID: 3ae9ca4569b5
Revises: 48034588fff8
Create Date: 2026-08-28 17:22:09.172768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ae9ca4569b5'
down_revision: Union[str, Sequence[str], None] = '48034588fff8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('providers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('kind', sa.String(length=32), nullable=False),
    sa.Column('base_url', sa.String(length=512), nullable=True),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_providers_owner_id'), 'providers', ['owner_id'], unique=False)
    op.create_table('api_keys',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('provider_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('secret', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_provider_id'), 'api_keys', ['provider_id'], unique=False)
    op.create_table('agents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('model', sa.String(length=128), nullable=False),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.Column('api_key_id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_api_key_id'), 'agents', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_agents_owner_id'), 'agents', ['owner_id'], unique=False)
    op.add_column('users', sa.Column('plan', sa.Enum('no_ai', 'system_ai', 'own_ai', name='user_plan', native_enum=False, length=16), server_default='no_ai', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'plan')
    op.drop_index(op.f('ix_agents_owner_id'), table_name='agents')
    op.drop_index(op.f('ix_agents_api_key_id'), table_name='agents')
    op.drop_table('agents')
    op.drop_index(op.f('ix_api_keys_provider_id'), table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_index(op.f('ix_providers_owner_id'), table_name='providers')
    op.drop_table('providers')
