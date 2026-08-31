from app.errors.ai import (
    AgentNotFoundError,
    AiAccessDeniedError,
    ApiKeyNotFoundError,
    InvalidEncryptionKeyError,
    OwnProviderNotAllowedError,
    ProviderNotFoundError,
    SecretDecryptionError,
    SecretEncryptionUnavailableError,
    SystemProviderRequiredError,
    SystemResourceReadOnlyError,
    UnknownAgentToolError,
)
from app.errors.auth import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
)
from app.errors.base import AppError
from app.errors.chat import (
    ChatNotFoundError,
    ChatResponseFailedError,
    MissingEmbeddingApiKeyError,
    MissingModelApiKeyError,
)
from app.errors.documents import AdrNotFoundError, StoryNotFoundError
from app.errors.handlers import register_error_handlers
from app.errors.health import DatabaseUnavailableError

__all__ = [
    "AdrNotFoundError",
    "AgentNotFoundError",
    "AiAccessDeniedError",
    "ApiKeyNotFoundError",
    "AppError",
    "ChatNotFoundError",
    "ChatResponseFailedError",
    "DatabaseUnavailableError",
    "EmailAlreadyRegisteredError",
    "InvalidCredentialsError",
    "InvalidEncryptionKeyError",
    "InvalidTokenError",
    "MissingEmbeddingApiKeyError",
    "MissingModelApiKeyError",
    "OwnProviderNotAllowedError",
    "ProviderNotFoundError",
    "SecretDecryptionError",
    "SecretEncryptionUnavailableError",
    "StoryNotFoundError",
    "SystemProviderRequiredError",
    "SystemResourceReadOnlyError",
    "UnknownAgentToolError",
    "UserNotFoundError",
    "register_error_handlers",
]
