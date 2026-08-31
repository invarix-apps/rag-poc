import logging
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any

import logfire
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import LogLevel, get_settings

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"

_CONSOLE_LEVELS: dict[LogLevel, logfire.LevelName] = {
    "CRITICAL": "fatal",
    "ERROR": "error",
    "WARNING": "warn",
    "INFO": "info",
    "DEBUG": "debug",
}

ECHOED_KEYS = ("input", "url")

logger = logging.getLogger("app")
request_logger = logging.getLogger("app.request")


class RequestLogger(logging.LoggerAdapter[logging.Logger]):
    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        request_id = (self.extra or {}).get("request_id")
        return f"[{request_id}] {msg}", kwargs


def drop_echoed_input(request: Any, attributes: dict[str, Any]) -> dict[str, Any]:
    errors = attributes.get("errors")
    if not isinstance(errors, list):
        return attributes

    attributes["errors"] = [
        {k: v for k, v in error.items() if k not in ECHOED_KEYS}
        if isinstance(error, Mapping)
        else error
        for error in errors
    ]
    return attributes


def configure_logging(app: FastAPI) -> None:
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))

    logger.setLevel(settings.log_level)
    logger.handlers = [handler]

    logfire.configure(
        service_name=settings.logfire_service_name,
        environment=settings.logfire_environment,
        token=settings.logfire_token,
        send_to_logfire="if-token-present",
        console=logfire.ConsoleOptions(
            min_log_level=_CONSOLE_LEVELS[settings.log_level]
        )
        if settings.logfire_console
        else False,
    )
    logfire.instrument_fastapi(app, request_attributes_mapper=drop_echoed_input)
    logfire.instrument_pydantic_ai()
    logger.addHandler(logfire.LogfireLoggingHandler())


def instrument_database(engine: AsyncEngine) -> None:
    logfire.instrument_sqlalchemy(engine=engine)
