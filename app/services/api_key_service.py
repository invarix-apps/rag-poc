import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApiKey, User
from app.errors import ApiKeyNotFoundError
from app.services.provider_service import ProviderService


class ApiKeyService:
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.__session = session
        self.__providers = ProviderService(session, user)

    async def list(self, provider_id: uuid.UUID) -> list[ApiKey]:
        provider = await self.__providers.get(provider_id)
        result = await self.__session.execute(
            select(ApiKey)
            .where(ApiKey.provider_id == provider.id)
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, provider_id: uuid.UUID, api_key_id: uuid.UUID) -> ApiKey:
        provider = await self.__providers.get(provider_id)
        result = await self.__session.execute(
            select(ApiKey).where(
                ApiKey.id == api_key_id, ApiKey.provider_id == provider.id
            )
        )
        api_key = result.scalar_one_or_none()
        if api_key is None:
            raise ApiKeyNotFoundError()
        return api_key

    async def create(self, provider_id: uuid.UUID, name: str, secret: str) -> ApiKey:
        provider = await self.__providers.get_owned(provider_id)
        api_key = ApiKey(provider_id=provider.id, name=name, secret=secret)
        self.__session.add(api_key)
        await self.__session.commit()
        await self.__session.refresh(api_key)
        return api_key

    async def update(
        self,
        provider_id: uuid.UUID,
        api_key_id: uuid.UUID,
        name: str | None = None,
        secret: str | None = None,
    ) -> ApiKey:
        await self.__providers.get_owned(provider_id)
        api_key = await self.get(provider_id, api_key_id)
        if name is not None:
            api_key.name = name
        if secret is not None:
            api_key.secret = secret
        await self.__session.commit()
        await self.__session.refresh(api_key)
        return api_key

    async def delete(self, provider_id: uuid.UUID, api_key_id: uuid.UUID) -> None:
        await self.__providers.get_owned(provider_id)
        api_key = await self.get(provider_id, api_key_id)
        await self.__session.delete(api_key)
        await self.__session.commit()
