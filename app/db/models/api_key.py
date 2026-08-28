import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class ApiKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128))
    secret: Mapped[str] = mapped_column(Text)

    @property
    def last4(self) -> str:
        return self.secret[-4:]
