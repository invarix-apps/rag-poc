import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.db.models import UserPlan


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    plan: UserPlan
    created_at: datetime
    updated_at: datetime
