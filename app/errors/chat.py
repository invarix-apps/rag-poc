from fastapi import status

from app.errors.base import AppError


class MissingModelApiKeyError(AppError):
    code = "missing_model_api_key"
    message = "Chave de API do modelo nao configurada"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class MissingEmbeddingApiKeyError(AppError):
    code = "missing_embedding_api_key"
    message = "GEMINI_API_KEY nao configurada"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
