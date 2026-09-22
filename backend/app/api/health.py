"""Health monitoring and environment status endpoint."""

from typing import Dict
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Service Health Check",
    description="Returns the operational status of FinNews AI and configuration health without exposing secrets.",
    response_model=Dict[str, object],
)
async def get_health() -> Dict[str, object]:
    """Check health and configuration availability."""
    return {
        "status": "healthy",
        "service": "FinNews AI",
        "news_api_configured": settings.is_news_api_configured,
        "groq_configured": settings.is_groq_configured,
    }
