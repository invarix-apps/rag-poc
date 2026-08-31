import uuid
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Adr, Embedding, Story, User
from app.errors import AdrNotFoundError, AppError, StoryNotFoundError
from app.services.embedding_service import EmbeddingService


class Document(Protocol):
    id: uuid.UUID
    name: str
    content: str
    created_by: uuid.UUID


class DocumentService[ModelT: (Adr, Story)]:
    def __init__(
        self,
        session: AsyncSession,
        user: User,
        model: type[ModelT],
        source_type: str,
        not_found_error: type[AppError],
    ) -> None:
        self.__session = session
        self.__user = user
        self.__model = model
        self.__source_type = source_type
        self.__not_found_error = not_found_error
        self.__embeddings = EmbeddingService(session)

    async def create(self, name: str, content: str) -> ModelT:
        document = self.__model(name=name, content=content, created_by=self.__user.id)
        self.__session.add(document)
        await self.__session.flush()
        await self.__embeddings.upsert(self.__source_type, document.id, content)
        await self.__session.commit()
        await self.__session.refresh(document)
        return document

    async def list(self) -> list[ModelT]:
        result = await self.__session.execute(
            select(self.__model)
            .where(self.__model.created_by == self.__user.id)
            .order_by(self.__model.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, document_id: uuid.UUID) -> ModelT:
        result = await self.__session.execute(
            select(self.__model).where(
                self.__model.id == document_id,
                self.__model.created_by == self.__user.id,
            )
        )
        document = result.scalar_one_or_none()
        if document is None:
            raise self.__not_found_error()
        return document

    async def update(
        self,
        document_id: uuid.UUID,
        name: str | None = None,
        content: str | None = None,
    ) -> ModelT:
        document = await self.get(document_id)
        if name is not None:
            document.name = name
        if content is not None:
            document.content = content
            await self.__embeddings.upsert(
                self.__source_type, document.id, document.content
            )
        await self.__session.commit()
        await self.__session.refresh(document)
        return document

    async def delete(self, document_id: uuid.UUID) -> None:
        document = await self.get(document_id)
        await self.__embeddings.delete_for(self.__source_type, document.id)
        await self.__session.delete(document)
        await self.__session.commit()

    async def embeddings(self, document_id: uuid.UUID) -> list[Embedding]:
        document = await self.get(document_id)
        return await self.__embeddings.list_for(self.__source_type, document.id)


def create_adr_service(session: AsyncSession, user: User) -> DocumentService[Adr]:
    return DocumentService(session, user, Adr, "adr", AdrNotFoundError)


def create_story_service(session: AsyncSession, user: User) -> DocumentService[Story]:
    return DocumentService(session, user, Story, "story", StoryNotFoundError)
