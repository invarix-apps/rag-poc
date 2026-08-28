from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from app.errors.base import AppError
from app.logging import logger


async def app_error_handler(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, AppError):
        raise exc

    if exc.status_code >= 500:
        logger.exception("%s: %s", exc.code, exc.message)
    else:
        logger.info("%s: %s", exc.code, exc.message)

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_payload(),
        headers=exc.headers,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
