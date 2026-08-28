import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Embedding
from app.lib.embeddings import embed_document


class EmbeddingService:
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def upsert(
        self, source_type: str, source_id: uuid.UUID, text: str
    ) -> Embedding:
        model_name, vector = await embed_document(text)

        existing = await self.__get(source_type, source_id, model_name)
        if existing is not None:
            existing.vector = vector
            await self.__session.flush()
            return existing

        embedding = Embedding(
            source_type=source_type,
            source_id=source_id,
            model=model_name,
            vector=vector,
        )
        self.__session.add(embedding)
        await self.__session.flush()
        return embedding

    async def list_for(
        self, source_type: str, source_id: uuid.UUID
    ) -> list[Embedding]:
        result = await self.__session.execute(
            select(Embedding).where(
                Embedding.source_type == source_type,
                Embedding.source_id == source_id,
            )
        )
        return list(result.scalars().all())

    async def delete_for(self, source_type: str, source_id: uuid.UUID) -> None:
        for embedding in await self.list_for(source_type, source_id):
            await self.__session.delete(embedding)
        await self.__session.flush()

    async def __get(
        self, source_type: str, source_id: uuid.UUID, model: str
    ) -> Embedding | None:
        result = await self.__session.execute(
            select(Embedding).where(
                Embedding.source_type == source_type,
                Embedding.source_id == source_id,
                Embedding.model == model,
            )
        )
        return result.scalar_one_or_none()
