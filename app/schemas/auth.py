from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.db.models import UserPlan


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    plan: UserPlan = UserPlan.NO_AI


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
