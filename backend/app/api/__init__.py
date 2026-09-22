"""API routers package for FinNews AI."""

from app.api.health import router as health_router
from app.api.news import router as news_router
from app.api.simplify import router as simplify_router

__all__ = ["health_router", "news_router", "simplify_router"]
