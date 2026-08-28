import uuid

from fastapi import APIRouter, status

from app.dependencies import CurrentUserDep, StoryServiceDep
from app.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    EmbeddingResponse,
)

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_story(
    payload: DocumentCreate, service: StoryServiceDep, user: CurrentUserDep
) -> DocumentResponse:
    story = await service.create(
        name=payload.name, content=payload.content, created_by=user.id
    )
    return DocumentResponse.model_validate(story)


@router.get("")
async def list_stories(
    service: StoryServiceDep, user: CurrentUserDep
) -> list[DocumentResponse]:
    return [DocumentResponse.model_validate(s) for s in await service.list()]


@router.get("/{story_id}")
async def get_story(
    story_id: uuid.UUID, service: StoryServiceDep, user: CurrentUserDep
) -> DocumentResponse:
    return DocumentResponse.model_validate(await service.get(story_id))


@router.patch("/{story_id}")
async def update_story(
    story_id: uuid.UUID,
    payload: DocumentUpdate,
    service: StoryServiceDep,
    user: CurrentUserDep,
) -> DocumentResponse:
    story = await service.update(story_id, name=payload.name, content=payload.content)
    return DocumentResponse.model_validate(story)


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: uuid.UUID, service: StoryServiceDep, user: CurrentUserDep
) -> None:
    await service.delete(story_id)


@router.get("/{story_id}/embeddings")
async def list_story_embeddings(
    story_id: uuid.UUID, service: StoryServiceDep, user: CurrentUserDep
) -> list[EmbeddingResponse]:
    return [
        EmbeddingResponse.model_validate(e) for e in await service.embeddings(story_id)
    ]
