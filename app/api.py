from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal

import logfire
from fastapi import FastAPI, HTTPException, WebSocket, status
from pydantic import BaseModel
from sqlalchemy import text

from app.db.session import create_engine, create_session_factory
from app.dependencies import ChatServiceDep, SessionDep
from app.logging import configure_logging, instrument_database, logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    engine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    instrument_database(engine)
    logger.info("app iniciada")

    try:
        yield
    finally:
        await engine.dispose()
        logger.info("app encerrada")


app = FastAPI(lifespan=lifespan)
configure_logging(app)


class HealthResponse(BaseModel):
    status: Literal["healthy"]


@app.get("/health")
async def health(session: SessionDep) -> HealthResponse:
    conn = await session.connection()
    db_health = (await conn.execute(text("SELECT 1;"))).fetchone()
    logfire.debug(str(db_health))
    if not db_health or not db_health[0] == 1:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return HealthResponse(status="healthy")


@app.websocket("/chat")
async def chat_room(websocket: WebSocket, chat_service: ChatServiceDep) -> None:

    async def on_response(message: str):
        await websocket.send_json({"type": "delta", "text": message})

    async def on_done():
        await websocket.send_json({"type": "done"})

    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        await chat_service.send_message(
            input=data, on_response=on_response, on_done=on_done
        )
