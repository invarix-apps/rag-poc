import uuid
from collections.abc import Sequence

from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentConfig, ApiKey, Provider, User, UserPlan
from app.errors import (
    AgentNotFoundError,
    AiAccessDeniedError,
    ApiKeyNotFoundError,
    SystemProviderRequiredError,
    SystemResourceReadOnlyError,
)
from app.services.tool_factory import parse_tool


class AgentService:
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.__session = session
        self.__user = user

    async def list(self) -> list[AgentConfig]:
        self.__require_ai()
        result = await self.__session.execute(
            select(AgentConfig)
            .where(self.__visible())
            .order_by(AgentConfig.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, agent_id: uuid.UUID) -> AgentConfig:
        self.__require_ai()
        result = await self.__session.execute(
            select(AgentConfig).where(AgentConfig.id == agent_id, self.__visible())
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError()
        return agent

    async def create(
        self,
        name: str,
        model: str,
        api_key_id: uuid.UUID,
        instructions: str | None = None,
        tools: Sequence[str] = (),
    ) -> AgentConfig:
        self.__require_ai()
        await self.resolve_usable_key(api_key_id)

        agent = AgentConfig(
            name=name,
            model=model,
            api_key_id=api_key_id,
            instructions=instructions,
            tools=self.__parse_tools(tools),
            owner_id=self.__user.id,
        )
        self.__session.add(agent)
        await self.__session.commit()
        await self.__session.refresh(agent)
        return agent

    async def update(
        self,
        agent_id: uuid.UUID,
        name: str | None = None,
        model: str | None = None,
        api_key_id: uuid.UUID | None = None,
        instructions: str | None = None,
        tools: Sequence[str] | None = None,
    ) -> AgentConfig:
        agent = await self.__get_owned(agent_id)
        if name is not None:
            agent.name = name
        if model is not None:
            agent.model = model
        if api_key_id is not None:
            await self.resolve_usable_key(api_key_id)
            agent.api_key_id = api_key_id
        if instructions is not None:
            agent.instructions = instructions
        if tools is not None:
            agent.tools = self.__parse_tools(tools)
        await self.__session.commit()
        await self.__session.refresh(agent)
        return agent

    async def delete(self, agent_id: uuid.UUID) -> None:
        agent = await self.__get_owned(agent_id)
        await self.__session.delete(agent)
        await self.__session.commit()

    def __parse_tools(self, tools: Sequence[str]) -> list[str]:
        return [parse_tool(name).value for name in dict.fromkeys(tools)]

    async def __get_owned(self, agent_id: uuid.UUID) -> AgentConfig:
        agent = await self.get(agent_id)
        if agent.owner_id is None:
            raise SystemResourceReadOnlyError()
        return agent

    async def resolve_usable_key(
        self, api_key_id: uuid.UUID
    ) -> tuple[ApiKey, Provider]:
        result = await self.__session.execute(
            select(ApiKey, Provider)
            .join(Provider, Provider.id == ApiKey.provider_id)
            .where(
                ApiKey.id == api_key_id,
                or_(
                    Provider.owner_id.is_(None),
                    Provider.owner_id == self.__user.id,
                ),
            )
        )
        row = result.one_or_none()
        if row is None:
            raise ApiKeyNotFoundError()

        api_key, provider = row.tuple()
        if self.__user.plan is UserPlan.SYSTEM_AI and provider.owner_id is not None:
            raise SystemProviderRequiredError()
        return api_key, provider

    def __require_ai(self) -> None:
        if self.__user.plan is UserPlan.NO_AI:
            raise AiAccessDeniedError()

    def __visible(self) -> ColumnElement[bool]:
        return or_(
            AgentConfig.owner_id.is_(None), AgentConfig.owner_id == self.__user.id
        )
