import uuid

from fastapi import APIRouter, status

from app.dependencies import AdrServiceDep, CurrentUserDep
from app.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    EmbeddingResponse,
)

router = APIRouter(prefix="/adrs", tags=["adrs"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_adr(
    payload: DocumentCreate, service: AdrServiceDep, user: CurrentUserDep
) -> DocumentResponse:
    adr = await service.create(
        name=payload.name, content=payload.content, created_by=user.id
    )
    return DocumentResponse.model_validate(adr)


@router.get("")
async def list_adrs(
    service: AdrServiceDep, user: CurrentUserDep
) -> list[DocumentResponse]:
    return [DocumentResponse.model_validate(a) for a in await service.list()]


@router.get("/{adr_id}")
async def get_adr(
    adr_id: uuid.UUID, service: AdrServiceDep, user: CurrentUserDep
) -> DocumentResponse:
    return DocumentResponse.model_validate(await service.get(adr_id))


@router.patch("/{adr_id}")
async def update_adr(
    adr_id: uuid.UUID,
    payload: DocumentUpdate,
    service: AdrServiceDep,
    user: CurrentUserDep,
) -> DocumentResponse:
    adr = await service.update(adr_id, name=payload.name, content=payload.content)
    return DocumentResponse.model_validate(adr)


@router.delete("/{adr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adr(
    adr_id: uuid.UUID, service: AdrServiceDep, user: CurrentUserDep
) -> None:
    await service.delete(adr_id)


@router.get("/{adr_id}/embeddings")
async def list_adr_embeddings(
    adr_id: uuid.UUID, service: AdrServiceDep, user: CurrentUserDep
) -> list[EmbeddingResponse]:
    return [
        EmbeddingResponse.model_validate(e) for e in await service.embeddings(adr_id)
    ]
