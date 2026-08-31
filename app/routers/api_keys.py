import uuid

from fastapi import APIRouter, status

from app.dependencies import ApiKeyServiceDep
from app.schemas import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate

router = APIRouter(prefix="/providers/{provider_id}/api-keys", tags=["api-keys"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    provider_id: uuid.UUID, payload: ApiKeyCreate, service: ApiKeyServiceDep
) -> ApiKeyResponse:
    api_key = await service.create(
        provider_id, name=payload.name, secret=payload.secret.get_secret_value()
    )
    return ApiKeyResponse.model_validate(api_key)


@router.get("")
async def list_api_keys(
    provider_id: uuid.UUID, service: ApiKeyServiceDep
) -> list[ApiKeyResponse]:
    return [ApiKeyResponse.model_validate(k) for k in await service.list(provider_id)]


@router.get("/{api_key_id}")
async def get_api_key(
    provider_id: uuid.UUID, api_key_id: uuid.UUID, service: ApiKeyServiceDep
) -> ApiKeyResponse:
    return ApiKeyResponse.model_validate(await service.get(provider_id, api_key_id))


@router.patch("/{api_key_id}")
async def update_api_key(
    provider_id: uuid.UUID,
    api_key_id: uuid.UUID,
    payload: ApiKeyUpdate,
    service: ApiKeyServiceDep,
) -> ApiKeyResponse:
    api_key = await service.update(
        provider_id,
        api_key_id,
        name=payload.name,
        secret=payload.secret.get_secret_value()
        if payload.secret is not None
        else None,
    )
    return ApiKeyResponse.model_validate(api_key)


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider_id: uuid.UUID, api_key_id: uuid.UUID, service: ApiKeyServiceDep
) -> None:
    await service.delete(provider_id, api_key_id)
