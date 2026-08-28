import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Adr, Story, User
from app.errors import AppError, InvalidTokenError, UserNotFoundError
from app.lib.security import decode_access_token
from app.logging import RequestLogger, logger, request_logger
from app.services import (
    AgentService,
    ApiKeyService,
    AuthService,
    ChatService,
    DocumentService,
    ProviderService,
    create_adr_service,
    create_story_service,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_logger(request: Request) -> RequestLogger:
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    return RequestLogger(request_logger, {"request_id": request_id})


LoggerDep = Annotated[RequestLogger, Depends(get_logger)]


def get_chat_service() -> ChatService:
    return ChatService()


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    user_id = decode_access_token(token)
    user = await auth_service.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_ws_session(websocket: WebSocket) -> AsyncGenerator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = (
        websocket.app.state.session_factory
    )
    async with session_factory() as session:
        yield session


WsSessionDep = Annotated[AsyncSession, Depends(get_ws_session)]


def get_ws_auth_service(session: WsSessionDep) -> AuthService:
    return AuthService(session)


WsAuthServiceDep = Annotated[AuthService, Depends(get_ws_auth_service)]


async def get_ws_current_user(
    websocket: WebSocket,
    auth_service: WsAuthServiceDep,
    token: str | None = None,
) -> User:
    try:
        header = websocket.headers.get("authorization")
        if header and header.lower().startswith("bearer "):
            raw_token = header[7:]
        elif token:
            raw_token = token
        else:
            raise InvalidTokenError()

        user_id = decode_access_token(raw_token)
        user = await auth_service.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
    except AppError as exc:
        logger.info("%s: %s", exc.code, exc.message)
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason=exc.code
        ) from exc


WsCurrentUserDep = Annotated[User, Depends(get_ws_current_user)]


def get_adr_service(session: SessionDep) -> DocumentService[Adr]:
    return create_adr_service(session)


def get_story_service(session: SessionDep) -> DocumentService[Story]:
    return create_story_service(session)


AdrServiceDep = Annotated[DocumentService[Adr], Depends(get_adr_service)]
StoryServiceDep = Annotated[DocumentService[Story], Depends(get_story_service)]


def get_provider_service(session: SessionDep, user: CurrentUserDep) -> ProviderService:
    return ProviderService(session, user)


ProviderServiceDep = Annotated[ProviderService, Depends(get_provider_service)]


def get_api_key_service(session: SessionDep, user: CurrentUserDep) -> ApiKeyService:
    return ApiKeyService(session, user)


ApiKeyServiceDep = Annotated[ApiKeyService, Depends(get_api_key_service)]


def get_agent_service(session: SessionDep, user: CurrentUserDep) -> AgentService:
    return AgentService(session, user)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
