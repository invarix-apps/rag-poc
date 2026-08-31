from app.routers import (
    adrs,
    agents,
    auth,
    chats,
    health,
    providers,
    stories,
)

ROUTERS = [
    health.router,
    auth.router,
    auth.users_router,
    providers.router,
    agents.router,
    adrs.router,
    stories.router,
    chats.router,
]

__all__ = [
    "ROUTERS",
    "adrs",
    "agents",
    "auth",
    "chats",
    "health",
    "providers",
    "stories",
]
