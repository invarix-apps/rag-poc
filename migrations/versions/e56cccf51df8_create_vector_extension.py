from collections.abc import Sequence

from alembic import op

revision: str = "e56cccf51df8"
down_revision: str | Sequence[str] | None = "bd26ea920911"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
