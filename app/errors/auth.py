from fastapi import status

from app.errors.base import AppError

_BEARER_HEADERS = {"WWW-Authenticate": "Bearer"}


class EmailAlreadyRegisteredError(AppError):
    code = "email_already_registered"
    message = "Email ja cadastrado"
    status_code = status.HTTP_409_CONFLICT


class InvalidCredentialsError(AppError):
    code = "invalid_credentials"
    message = "Credenciais invalidas"
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = _BEARER_HEADERS


class InvalidTokenError(AppError):
    code = "invalid_token"
    message = "Token invalido ou expirado"
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = _BEARER_HEADERS


class UserNotFoundError(AppError):
    code = "user_not_found"
    message = "Usuario nao encontrado"
    status_code = status.HTTP_404_NOT_FOUND
