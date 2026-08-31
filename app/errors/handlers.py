from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from app.errors.base import AppError
from app.logging import logger

ECHOED_KEYS = ("input", "url")


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


async def validation_error_handler(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, RequestValidationError):
        raise exc

    details: list[dict[str, Any]] = [
        {k: v for k, v in error.items() if k not in ECHOED_KEYS}
        for error in exc.errors()
    ]
    logger.info("validation_error: %s", [d.get("loc") for d in details])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(
            {
                "code": "validation_error",
                "message": "Payload invalido",
                "details": details,
            }
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
