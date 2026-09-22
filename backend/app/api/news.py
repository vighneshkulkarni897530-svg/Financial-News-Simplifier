"""Financial news endpoints providing categorized retrieval, search, and deduplication."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.news_schema import NewsResponse
from app.services.news_service import NewsServiceException, news_service

router = APIRouter(prefix="/api/news", tags=["Financial News"])


@router.get(
    "",
    summary="Retrieve Financial News",
    description="Fetches verified, normalized, and deduplicated financial news articles with category and search filtering.",
    response_model=NewsResponse,
)
async def get_news(
    query: Optional[str] = Query(None, description="Search keyword or ticker symbol (e.g. 'Apple', 'interest rates')"),
    category: Optional[str] = Query("all", description="Category: 'all', 'markets', 'economy', 'business', 'technology'"),
    page: int = Query(1, ge=1, le=20, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of articles per page"),
) -> NewsResponse:
    """Retrieve financial news articles matching parameters."""
    try:
        return await news_service.get_financial_news(
            query=query,
            category=category,
            page=page,
            page_size=page_size,
        )
    except NewsServiceException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get(
    "/search",
    summary="Search Financial News",
    description="Convenience search endpoint for querying specific financial keywords, tickers, or economic subjects.",
    response_model=NewsResponse,
)
async def search_news(
    query: str = Query(..., min_length=1, description="Search query string"),
    page: int = Query(1, ge=1, le=20, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of results per page"),
) -> NewsResponse:
    """Search financial news by query."""
    try:
        return await news_service.get_financial_news(
            query=query,
            category=None,
            page=page,
            page_size=page_size,
        )
    except NewsServiceException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )
