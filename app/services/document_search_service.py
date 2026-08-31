import uuid
from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Adr, Embedding, Story, User
from app.lib.embeddings import embed_query

MAX_RESULTS = 20


@dataclass(frozen=True, kw_only=True)
class DocumentMatch:
    id: uuid.UUID
    name: str
    content: str
    score: float
    rank: int


class DocumentSearchService:
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.__session = session
        self.__user = user

    async def search_adrs(self, query: str, limit: int) -> list[DocumentMatch]:
        return await self.__search(Adr, "adr", query, limit)

    async def search_stories(self, query: str, limit: int) -> list[DocumentMatch]:
        return await self.__search(Story, "story", query, limit)

    async def __search(
        self,
        model_type: type[Adr | Story],
        source_type: str,
        query: str,
        limit: int,
    ) -> list[DocumentMatch]:
        _, vector = await embed_query(query)
        distance = Embedding.vector.cosine_distance(vector).label("distance")

        result = await self.__session.execute(
            select(model_type, distance)
            .join(
                Embedding,
                and_(
                    Embedding.source_id == model_type.id,
                    Embedding.source_type == source_type,
                ),
            )
            .where(
                model_type.created_by == self.__user.id,
                Embedding.model == get_settings().embedding_model,
            )
            .order_by(distance)
            .limit(min(limit, MAX_RESULTS))
        )

        return [
            DocumentMatch(
                id=document.id,
                name=document.name,
                content=document.content,
                score=round(1 - float(document_distance), 4),
                rank=rank,
            )
            for rank, (document, document_distance) in enumerate(result.all(), start=1)
        ]
