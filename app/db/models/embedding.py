import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.config import get_settings
from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Embedding(Base, TimestampMixin):
    __tablename__ = "embeddings"
    __table_args__ = (
        UniqueConstraint(
            "source_type", "source_id", "model", name="uq_embeddings_source_model"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    model: Mapped[str] = mapped_column(String(128))
    vector: Mapped[list[float]] = mapped_column(
        Vector(get_settings().embedding_dimensions)
    )
