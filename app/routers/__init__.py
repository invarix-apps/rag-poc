from app.routers import (
    adrs,
    agents,
    api_keys,
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
    api_keys.router,
    agents.router,
    adrs.router,
    stories.router,
    chats.router,
]

__all__ = [
    "ROUTERS",
    "adrs",
    "agents",
    "api_keys",
    "auth",
    "chats",
    "health",
    "providers",
    "stories",
]
