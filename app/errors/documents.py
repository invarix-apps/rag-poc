from fastapi import status

from app.errors.base import AppError


class AdrNotFoundError(AppError):
    code = "adr_not_found"
    message = "ADR nao encontrado"
    status_code = status.HTTP_404_NOT_FOUND


class StoryNotFoundError(AppError):
    code = "story_not_found"
    message = "Story nao encontrada"
    status_code = status.HTTP_404_NOT_FOUND
