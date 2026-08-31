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


class ChatNotFoundError(AppError):
    code = "chat_not_found"
    message = "Chat nao encontrado"
    status_code = status.HTTP_404_NOT_FOUND


class ChatResponseFailedError(AppError):
    code = "chat_response_failed"
    message = "Falha ao gerar resposta"
    status_code = status.HTTP_502_BAD_GATEWAY
