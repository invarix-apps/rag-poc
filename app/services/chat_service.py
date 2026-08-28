from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from pydantic_ai import ModelMessage

from app.config import get_settings
from app.lib.agent import create_agent


@dataclass(
    kw_only=True,
)
class ChatMessage:
    actor: Literal["bot", "user"]
    content: str


class ChatService:
    def __init__(self) -> None:
        key = get_settings().open_router_api_key
        if not key:
            raise RuntimeError("AI API Key")
        self.__agent = create_agent(
            "openrouter:deepseek/deepseek-v4-pro-0813", api_key=key
        )
        self.__history: list[ModelMessage] = []

    async def send_message(
        self,
        input: str,
        on_response: Callable[[str], Awaitable[None]],
        on_done: Callable[[], Awaitable[None]],
    ):
        async with self.__agent.run_stream(
            user_prompt=input, message_history=self.__history
        ) as result:
            async for delta in result.stream_text(delta=True):
                await on_response(delta)
            self.__history = result.all_messages()
            await on_done()
