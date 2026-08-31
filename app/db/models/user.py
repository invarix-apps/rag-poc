import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import UserPlan, enum_values
from app.db.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    plan: Mapped[UserPlan] = mapped_column(
        Enum(
            UserPlan,
            name="user_plan",
            native_enum=False,
            length=16,
            values_callable=enum_values,
        ),
        default=UserPlan.NO_AI,
        server_default=UserPlan.NO_AI.value,
    )
