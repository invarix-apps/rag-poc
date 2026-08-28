from typing import Literal

from pydantic import BaseModel


class ChatDelta(BaseModel):
    type: Literal["delta"] = "delta"
    text: str


class ChatDone(BaseModel):
    type: Literal["done"] = "done"
