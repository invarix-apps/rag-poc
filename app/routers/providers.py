import uuid

from fastapi import APIRouter, status

from app.dependencies import ProviderServiceDep
from app.schemas import ProviderCreate, ProviderResponse, ProviderUpdate

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_provider(
    payload: ProviderCreate, service: ProviderServiceDep
) -> ProviderResponse:
    provider = await service.create(
        name=payload.name, kind=payload.kind, base_url=payload.base_url
    )
    return ProviderResponse.model_validate(provider)


@router.get("")
async def list_providers(service: ProviderServiceDep) -> list[ProviderResponse]:
    return [ProviderResponse.model_validate(p) for p in await service.list()]


@router.get("/{provider_id}")
async def get_provider(
    provider_id: uuid.UUID, service: ProviderServiceDep
) -> ProviderResponse:
    return ProviderResponse.model_validate(await service.get(provider_id))


@router.patch("/{provider_id}")
async def update_provider(
    provider_id: uuid.UUID, payload: ProviderUpdate, service: ProviderServiceDep
) -> ProviderResponse:
    provider = await service.update(
        provider_id, name=payload.name, kind=payload.kind, base_url=payload.base_url
    )
    return ProviderResponse.model_validate(provider)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: uuid.UUID, service: ProviderServiceDep
) -> None:
    await service.delete(provider_id)
