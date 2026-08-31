import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    kind: str = Field(min_length=1, max_length=32)
    base_url: str | None = Field(default=None, max_length=512)


class ProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    kind: str | None = Field(default=None, min_length=1, max_length=32)
    base_url: str | None = Field(default=None, max_length=512)


class ProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    kind: str
    base_url: str | None
    owner_id: uuid.UUID | None
    is_system: bool
    created_at: datetime
    updated_at: datetime


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    secret: SecretStr = Field(min_length=8)


class ApiKeyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    secret: SecretStr | None = Field(default=None, min_length=8)


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider_id: uuid.UUID
    name: str
    last4: str
    created_at: datetime
    updated_at: datetime


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    api_key_id: uuid.UUID
    instructions: str | None = Field(default=None)


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    model: str | None = Field(default=None, min_length=1, max_length=128)
    api_key_id: uuid.UUID | None = Field(default=None)
    instructions: str | None = Field(default=None)


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    model: str
    instructions: str | None
    api_key_id: uuid.UUID
    owner_id: uuid.UUID | None
    is_system: bool
    created_at: datetime
    updated_at: datetime
