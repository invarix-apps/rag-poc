import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import MessageRole


class ChatCreate(BaseModel):
    agent_id: uuid.UUID
    title: str = Field(default="Novo chat", min_length=1, max_length=255)


class ChatUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    agent_id: uuid.UUID | None = Field(default=None)


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    user_id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chat_id: uuid.UUID
    role: MessageRole
    content: str
    created_at: datetime


class ChatDelta(BaseModel):
    type: Literal["delta"] = "delta"
    text: str


class ChatDone(BaseModel):
    type: Literal["done"] = "done"
    message_id: uuid.UUID


class ChatError(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
