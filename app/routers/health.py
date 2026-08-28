import logfire
from fastapi import APIRouter
from sqlalchemy import text

from app.dependencies import SessionDep
from app.errors import DatabaseUnavailableError
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(session: SessionDep) -> HealthResponse:
    conn = await session.connection()
    db_health = (await conn.execute(text("SELECT 1;"))).fetchone()
    logfire.debug(str(db_health))
    if not db_health or not db_health[0] == 1:
        raise DatabaseUnavailableError()
    return HealthResponse(status="healthy")
