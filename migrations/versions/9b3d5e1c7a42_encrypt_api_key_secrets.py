"""encrypt api key secrets

Revision ID: 9b3d5e1c7a42
Revises: 7c1f2a9b4d30
Create Date: 2026-08-31 14:10:00.000000

"""
import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.lib.crypto import seal, unseal


# revision identifiers, used by Alembic.
revision: str = '9b3d5e1c7a42'
down_revision: Union[str, Sequence[str], None] = '7c1f2a9b4d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEALED = re.compile(r"^v\d+:")

SELECT = sa.text("select id, provider_id, secret from api_keys")
UPDATE = sa.text(
    "update api_keys set secret = :secret, last4 = :last4 where id = :id"
)


def upgrade() -> None:
    op.add_column('api_keys', sa.Column('last4', sa.String(length=4), nullable=True))

    bind = op.get_bind()
    for row in bind.execute(SELECT).mappings().all():
        if SEALED.match(row["secret"]):
            secret = unseal(row["secret"], row["provider_id"], row["id"])
            sealed = row["secret"]
        else:
            secret = row["secret"]
            sealed = seal(secret, row["provider_id"], row["id"])
        bind.execute(
            UPDATE, {"secret": sealed, "last4": secret[-4:], "id": row["id"]}
        )

    op.alter_column('api_keys', 'last4', nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    for row in bind.execute(SELECT).mappings().all():
        if not SEALED.match(row["secret"]):
            continue
        secret = unseal(row["secret"], row["provider_id"], row["id"])
        bind.execute(
            sa.text("update api_keys set secret = :secret where id = :id"),
            {"secret": secret, "id": row["id"]},
        )

    op.drop_column('api_keys', 'last4')
