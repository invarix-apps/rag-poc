from fastapi import APIRouter, WebSocket

from app.dependencies import ChatServiceDep, WsCurrentUserDep
from app.logging import logger
from app.schemas import ChatDelta, ChatDone

router = APIRouter(tags=["chats"])


@router.websocket("/chat")
async def chat_room(
    websocket: WebSocket, chat_service: ChatServiceDep, user: WsCurrentUserDep
) -> None:
    async def on_response(message: str) -> None:
        await websocket.send_json(ChatDelta(text=message).model_dump())

    async def on_done() -> None:
        await websocket.send_json(ChatDone().model_dump())

    await websocket.accept()
    logger.info("chat aberto por %s", user.email)
    while True:
        data = await websocket.receive_text()

        await chat_service.send_message(
            input=data, on_response=on_response, on_done=on_done
        )
