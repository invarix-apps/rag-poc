from typing import Annotated, Literal

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.db.models import UserPlan


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)
    plan: UserPlan = UserPlan.NO_AI


class LoginForm(BaseModel):
    grant_type: Annotated[Literal["password"] | None, Form()] = None
    username: Annotated[str, Form()]
    password: Annotated[SecretStr, Form()]
    scope: Annotated[str, Form()] = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
