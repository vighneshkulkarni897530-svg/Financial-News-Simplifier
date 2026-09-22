"""Schemas package for FinNews AI."""

from app.schemas.news_schema import Article, ErrorResponse, NewsResponse
from app.schemas.summary_schema import (
    BatchSimplifyItem,
    BatchSimplifyRequest,
    BatchSimplifyResponse,
    FinancialTerm,
    SimplificationResult,
    SimplifyRequest,
    SimplifyResponse,
)

__all__ = [
    "Article",
    "NewsResponse",
    "ErrorResponse",
    "FinancialTerm",
    "SimplificationResult",
    "SimplifyRequest",
    "SimplifyResponse",
    "BatchSimplifyRequest",
    "BatchSimplifyItem",
    "BatchSimplifyResponse",
]
