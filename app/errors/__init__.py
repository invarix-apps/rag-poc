from app.errors.auth import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
)
from app.errors.base import AppError
from app.errors.chat import MissingEmbeddingApiKeyError, MissingModelApiKeyError
from app.errors.documents import AdrNotFoundError, StoryNotFoundError
from app.errors.handlers import register_error_handlers
from app.errors.health import DatabaseUnavailableError

__all__ = [
    "AdrNotFoundError",
    "AppError",
    "DatabaseUnavailableError",
    "EmailAlreadyRegisteredError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "MissingEmbeddingApiKeyError",
    "MissingModelApiKeyError",
    "StoryNotFoundError",
    "UserNotFoundError",
    "register_error_handlers",
]
