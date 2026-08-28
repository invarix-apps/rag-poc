from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import create_engine, create_session_factory
from app.errors import register_error_handlers
from app.logging import configure_logging, instrument_database, logger
from app.routers import ROUTERS


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    engine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    instrument_database(engine)
    logger.info("app iniciada")

    try:
        yield
    finally:
        await engine.dispose()
        logger.info("app encerrada")


app = FastAPI(lifespan=lifespan)
configure_logging(app)
register_error_handlers(app)

for router in ROUTERS:
    app.include_router(router)
