from app.routers import adrs, auth, chats, health, stories

ROUTERS = [
    health.router,
    auth.router,
    auth.users_router,
    adrs.router,
    stories.router,
    chats.router,
]

__all__ = ["ROUTERS", "adrs", "auth", "chats", "health", "stories"]
