import uuid

from fastapi import APIRouter, status

from app.dependencies import ApiKeyServiceDep, ProviderServiceDep
from app.schemas import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyUpsert,
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)
from app.services.provider_service import ApiKeyInput

router = APIRouter(prefix="/providers", tags=["providers"])


def to_inputs(payload: list[ApiKeyCreate] | list[ApiKeyUpsert]) -> list[ApiKeyInput]:
    return [
        ApiKeyInput(
            id=getattr(entry, "id", None),
            name=entry.name,
            secret=entry.secret.get_secret_value()
            if entry.secret is not None
            else None,
        )
        for entry in payload
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_provider(
    payload: ProviderCreate, service: ProviderServiceDep
) -> ProviderResponse:
    provider = await service.create(
        name=payload.name,
        kind=payload.kind,
        base_url=payload.base_url,
        api_keys=to_inputs(payload.api_keys),
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
        provider_id,
        name=payload.name,
        kind=payload.kind,
        base_url=payload.base_url,
        api_keys=to_inputs(payload.api_keys) if payload.api_keys is not None else None,
    )
    return ProviderResponse.model_validate(provider)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: uuid.UUID, service: ProviderServiceDep) -> None:
    await service.delete(provider_id)


@router.get("/{provider_id}/api-keys")
async def list_api_keys(
    provider_id: uuid.UUID, service: ApiKeyServiceDep
) -> list[ApiKeyResponse]:
    return [ApiKeyResponse.model_validate(k) for k in await service.list(provider_id)]


@router.get("/{provider_id}/api-keys/{api_key_id}")
async def get_api_key(
    provider_id: uuid.UUID, api_key_id: uuid.UUID, service: ApiKeyServiceDep
) -> ApiKeyResponse:
    return ApiKeyResponse.model_validate(await service.get(provider_id, api_key_id))


@router.delete(
    "/{provider_id}/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_api_key(
    provider_id: uuid.UUID, api_key_id: uuid.UUID, service: ApiKeyServiceDep
) -> None:
    await service.delete(provider_id, api_key_id)
