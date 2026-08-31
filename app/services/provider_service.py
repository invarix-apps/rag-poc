import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApiKey, Provider, User, UserPlan
from app.errors import (
    ApiKeyNotFoundError,
    OwnProviderNotAllowedError,
    ProviderNotFoundError,
    SystemResourceReadOnlyError,
)
from app.lib.crypto import seal


@dataclass(frozen=True, kw_only=True)
class ApiKeyInput:
    id: uuid.UUID | None = None
    name: str | None = None
    secret: str | None = None


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
        self,
        name: str,
        kind: str,
        base_url: str | None = None,
        api_keys: Sequence[ApiKeyInput] = (),
    ) -> Provider:
        if self.__user.plan is not UserPlan.OWN_AI:
            raise OwnProviderNotAllowedError()

        provider = Provider(
            id=uuid.uuid7(),
            name=name,
            kind=kind,
            base_url=base_url,
            owner_id=self.__user.id,
        )
        self.__session.add(provider)
        self.__upsert_keys(provider, api_keys)
        await self.__session.commit()
        await self.__session.refresh(provider)
        return provider

    async def update(
        self,
        provider_id: uuid.UUID,
        name: str | None = None,
        kind: str | None = None,
        base_url: str | None = None,
        api_keys: Sequence[ApiKeyInput] | None = None,
    ) -> Provider:
        provider = await self.get_owned(provider_id)
        if name is not None:
            provider.name = name
        if kind is not None:
            provider.kind = kind
        if base_url is not None:
            provider.base_url = base_url
        if api_keys is not None:
            self.__upsert_keys(provider, api_keys)
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

    def __upsert_keys(
        self, provider: Provider, api_keys: Sequence[ApiKeyInput]
    ) -> None:
        existing = {key.id: key for key in provider.api_keys}
        for entry in api_keys:
            if entry.id is None:
                self.__add_key(provider, entry)
                continue

            api_key = existing.get(entry.id)
            if api_key is None:
                raise ApiKeyNotFoundError()
            if entry.name is not None:
                api_key.name = entry.name
            if entry.secret is not None:
                api_key.secret = seal(entry.secret, provider.id, api_key.id)
                api_key.last4 = entry.secret[-4:]

    def __add_key(self, provider: Provider, entry: ApiKeyInput) -> None:
        if entry.name is None or entry.secret is None:
            raise ApiKeyNotFoundError(
                "name e secret sao obrigatorios para criar uma chave"
            )

        api_key_id = uuid.uuid7()
        provider.api_keys.append(
            ApiKey(
                id=api_key_id,
                provider_id=provider.id,
                name=entry.name,
                secret=seal(entry.secret, provider.id, api_key_id),
                last4=entry.secret[-4:],
            )
        )

    def __visible(self) -> ColumnElement[bool]:
        return or_(Provider.owner_id.is_(None), Provider.owner_id == self.__user.id)
