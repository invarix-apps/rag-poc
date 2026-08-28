from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import AuthServiceDep, CurrentUserDep
from app.schemas import RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, auth_service: AuthServiceDep
) -> UserResponse:
    user = await auth_service.register(
        name=payload.name, email=payload.email, password=payload.password
    )
    return UserResponse.model_validate(user)


@router.post("/login")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> TokenResponse:
    token = await auth_service.login(form.username, form.password)
    return TokenResponse(access_token=token)


@users_router.get("/me")
async def me(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user)
