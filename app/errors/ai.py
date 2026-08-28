from fastapi import status

from app.errors.base import AppError


class ProviderNotFoundError(AppError):
    code = "provider_not_found"
    message = "Provider nao encontrado"
    status_code = status.HTTP_404_NOT_FOUND


class ApiKeyNotFoundError(AppError):
    code = "api_key_not_found"
    message = "Chave de API nao encontrada"
    status_code = status.HTTP_404_NOT_FOUND


class AgentNotFoundError(AppError):
    code = "agent_not_found"
    message = "Agente nao encontrado"
    status_code = status.HTTP_404_NOT_FOUND


class SystemResourceReadOnlyError(AppError):
    code = "system_resource_read_only"
    message = "Recursos do sistema nao podem ser alterados"
    status_code = status.HTTP_403_FORBIDDEN


class AiAccessDeniedError(AppError):
    code = "ai_access_denied"
    message = "Plano sem acesso a IA"
    status_code = status.HTTP_403_FORBIDDEN


class OwnProviderNotAllowedError(AppError):
    code = "own_provider_not_allowed"
    message = "Plano nao permite providers proprios"
    status_code = status.HTTP_403_FORBIDDEN


class SystemProviderRequiredError(AppError):
    code = "system_provider_required"
    message = "Plano permite apenas chaves de providers do sistema"
    status_code = status.HTTP_403_FORBIDDEN
