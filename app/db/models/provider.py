import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Provider(Base, TimestampMixin):
    __tablename__ = "providers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    name: Mapped[str] = mapped_column(String(128))
    kind: Mapped[str] = mapped_column(String(32))
    base_url: Mapped[str | None] = mapped_column(String(512), default=None)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        default=None,
    )

    @property
    def is_system(self) -> bool:
        return self.owner_id is None
