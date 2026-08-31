import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.dependencies import ChatServiceDep, WsChatServiceDep, WsCurrentUserDep
from app.errors import AppError
from app.logging import logger
from app.schemas import (
    ChatCreate,
    ChatDelta,
    ChatDone,
    ChatError,
    ChatMessageResponse,
    ChatResponse,
    ChatUpdate,
)

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(payload: ChatCreate, service: ChatServiceDep) -> ChatResponse:
    chat = await service.create(agent_id=payload.agent_id, title=payload.title)
    return ChatResponse.model_validate(chat)


@router.get("")
async def list_chats(service: ChatServiceDep) -> list[ChatResponse]:
    return [ChatResponse.model_validate(c) for c in await service.list()]


@router.get("/{chat_id}")
async def get_chat(chat_id: uuid.UUID, service: ChatServiceDep) -> ChatResponse:
    return ChatResponse.model_validate(await service.get(chat_id))


@router.patch("/{chat_id}")
async def update_chat(
    chat_id: uuid.UUID, payload: ChatUpdate, service: ChatServiceDep
) -> ChatResponse:
    chat = await service.update(chat_id, title=payload.title, agent_id=payload.agent_id)
    return ChatResponse.model_validate(chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: uuid.UUID, service: ChatServiceDep) -> None:
    await service.delete(chat_id)


@router.get("/{chat_id}/messages")
async def list_messages(
    chat_id: uuid.UUID, service: ChatServiceDep
) -> list[ChatMessageResponse]:
    return [
        ChatMessageResponse.model_validate(m) for m in await service.messages(chat_id)
    ]


@router.websocket("/{chat_id}/ws")
async def chat_room(
    websocket: WebSocket,
    chat_id: uuid.UUID,
    chat_service: WsChatServiceDep,
    user: WsCurrentUserDep,
) -> None:
    async def on_response(message: str) -> None:
        await websocket.send_json(ChatDelta(text=message).model_dump())

    async def on_done(message_id: uuid.UUID) -> None:
        await websocket.send_json(
            ChatDone(message_id=message_id).model_dump(mode="json")
        )

    await websocket.accept()
    logger.info("chat %s aberto por %s", chat_id, user.email)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                await chat_service.send_message(
                    chat_id=chat_id,
                    input=data,
                    on_response=on_response,
                    on_done=on_done,
                )
            except AppError as exc:
                logger.info("%s: %s", exc.code, exc.message, exc_info=exc.__cause__)
                await websocket.send_json(
                    ChatError(code=exc.code, message=exc.message).model_dump()
                )
    except WebSocketDisconnect:
        logger.info("chat %s fechado por %s", chat_id, user.email)
