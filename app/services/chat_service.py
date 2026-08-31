import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentConfig, Chat, ChatMessage, MessageRole, User
from app.errors import AppError, ChatNotFoundError, ChatResponseFailedError
from app.lib.agent import create_agent
from app.lib.crypto import unseal
from app.services.agent_service import AgentService
from app.services.document_search_service import DocumentSearchService
from app.services.tool_factory import build_toolkit


class ChatService:
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.__session = session
        self.__user = user
        self.__agents = AgentService(session, user)

    async def create(self, agent_id: uuid.UUID, title: str) -> Chat:
        await self.__agents.get(agent_id)
        chat = Chat(title=title, user_id=self.__user.id, agent_id=agent_id)
        self.__session.add(chat)
        await self.__session.commit()
        await self.__session.refresh(chat)
        return chat

    async def list(self) -> list[Chat]:
        result = await self.__session.execute(
            select(Chat)
            .where(Chat.user_id == self.__user.id)
            .order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, chat_id: uuid.UUID) -> Chat:
        result = await self.__session.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == self.__user.id)
        )
        chat = result.scalar_one_or_none()
        if chat is None:
            raise ChatNotFoundError()
        return chat

    async def update(
        self,
        chat_id: uuid.UUID,
        title: str | None = None,
        agent_id: uuid.UUID | None = None,
    ) -> Chat:
        chat = await self.get(chat_id)
        if title is not None:
            chat.title = title
        if agent_id is not None:
            await self.__agents.get(agent_id)
            chat.agent_id = agent_id
        await self.__session.commit()
        await self.__session.refresh(chat)
        return chat

    async def delete(self, chat_id: uuid.UUID) -> None:
        chat = await self.get(chat_id)
        await self.__session.delete(chat)
        await self.__session.commit()

    async def messages(self, chat_id: uuid.UUID) -> list[ChatMessage]:
        chat = await self.get(chat_id)
        return await self.__list_messages(chat.id)

    async def send_message(
        self,
        chat_id: uuid.UUID,
        input: str,
        on_response: Callable[[str], Awaitable[None]],
        on_done: Callable[[uuid.UUID], Awaitable[None]],
    ) -> None:
        chat = await self.get(chat_id)
        agent = await self.__build_agent(chat.agent_id)
        history = self.__to_history(await self.__list_messages(chat.id))

        chunks: list[str] = []
        try:
            async with agent.run_stream(
                user_prompt=input, message_history=history
            ) as result:
                async for delta in result.stream_text(delta=True):
                    chunks.append(delta)
                    await on_response(delta)
        except AppError:
            raise
        except Exception as exc:
            raise ChatResponseFailedError() from exc

        answer = await self.__save_exchange(chat, input, "".join(chunks))
        await on_done(answer.id)

    async def __build_agent(self, agent_id: uuid.UUID) -> Agent[None, str]:
        config = await self.__agents.get(agent_id)
        api_key, base_url = await self.__resolve_key(config)
        toolkit = build_toolkit(
            config.tools, DocumentSearchService(self.__session, self.__user)
        )
        return create_agent(
            config.model,
            api_key=api_key,
            base_url=base_url,
            instructions=config.instructions,
            tools=toolkit.tools,
            capabilities=toolkit.capabilities,
        )

    async def __resolve_key(self, config: AgentConfig) -> tuple[str, str | None]:
        api_key, provider = await self.__agents.resolve_usable_key(config.api_key_id)
        secret = unseal(api_key.secret, api_key.provider_id, api_key.id)
        return secret, provider.base_url

    async def __list_messages(self, chat_id: uuid.UUID) -> list[ChatMessage]:
        result = await self.__session.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.id)
        )
        return list(result.scalars().all())

    async def __save_exchange(
        self, chat: Chat, prompt: str, answer: str
    ) -> ChatMessage:
        question = ChatMessage(chat_id=chat.id, role=MessageRole.USER, content=prompt)
        response = ChatMessage(
            chat_id=chat.id, role=MessageRole.ASSISTANT, content=answer
        )
        chat.updated_at = datetime.now(UTC)
        self.__session.add_all([question, response])
        await self.__session.commit()
        await self.__session.refresh(response)
        return response

    def __to_history(self, messages: list[ChatMessage]) -> list[ModelMessage]:
        history: list[ModelMessage] = []
        for message in messages:
            if message.role is MessageRole.USER:
                history.append(ModelRequest([UserPromptPart(message.content)]))
            else:
                history.append(ModelResponse([TextPart(message.content)]))
        return history
