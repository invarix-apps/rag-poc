from fastapi import status

from app.errors.base import AppError


class DatabaseUnavailableError(AppError):
    code = "database_unavailable"
    message = "Banco de dados indisponivel"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
