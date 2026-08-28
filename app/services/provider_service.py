import uuid

from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Provider, User, UserPlan
from app.errors import (
    OwnProviderNotAllowedError,
    ProviderNotFoundError,
    SystemResourceReadOnlyError,
)


class ProviderService:
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.__session = session
        self.__user = user

    async def list(self) -> list[Provider]:
        result = await self.__session.execute(
            select(Provider)
            .where(self.__visible())
            .order_by(Provider.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, provider_id: uuid.UUID) -> Provider:
        result = await self.__session.execute(
            select(Provider).where(Provider.id == provider_id, self.__visible())
        )
        provider = result.scalar_one_or_none()
        if provider is None:
            raise ProviderNotFoundError()
        return provider

    async def create(
        self, name: str, kind: str, base_url: str | None = None
    ) -> Provider:
        if self.__user.plan is not UserPlan.OWN_AI:
            raise OwnProviderNotAllowedError()

        provider = Provider(
            name=name, kind=kind, base_url=base_url, owner_id=self.__user.id
        )
        self.__session.add(provider)
        await self.__session.commit()
        await self.__session.refresh(provider)
        return provider

    async def update(
        self,
        provider_id: uuid.UUID,
        name: str | None = None,
        kind: str | None = None,
        base_url: str | None = None,
    ) -> Provider:
        provider = await self.get_owned(provider_id)
        if name is not None:
            provider.name = name
        if kind is not None:
            provider.kind = kind
        if base_url is not None:
            provider.base_url = base_url
        await self.__session.commit()
        await self.__session.refresh(provider)
        return provider

    async def delete(self, provider_id: uuid.UUID) -> None:
        provider = await self.get_owned(provider_id)
        await self.__session.delete(provider)
        await self.__session.commit()

    async def get_owned(self, provider_id: uuid.UUID) -> Provider:
        provider = await self.get(provider_id)
        if provider.owner_id is None:
            raise SystemResourceReadOnlyError()
        return provider

    def __visible(self) -> ColumnElement[bool]:
        return or_(Provider.owner_id.is_(None), Provider.owner_id == self.__user.id)
