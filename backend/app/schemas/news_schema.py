"""Pydantic schemas for news articles and news API responses."""

from typing import Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    """Normalized article model representing a single financial news story."""

    title: str = Field(..., description="Article headline")
    description: Optional[str] = Field(None, description="Short summary or description")
    content: Optional[str] = Field(None, description="Full or excerpted article content")
    source: str = Field(..., description="Source news outlet or publisher name")
    author: Optional[str] = Field(None, description="Author name if available")
    published_at: Optional[str] = Field(None, description="Publication timestamp ISO-8601 or string")
    url: str = Field(..., description="Canonical URL to original article")
    image_url: Optional[str] = Field(None, description="URL of article lead image")


class NewsResponse(BaseModel):
    """Standardized response payload for news queries."""

    status: str = Field("success", description="Status string: success or error")
    total_results: int = Field(0, description="Total count of retrieved articles")
    articles: List[Article] = Field(default_factory=list, description="List of normalized articles")
    query: Optional[str] = Field(None, description="Search query term used, if any")
    category: Optional[str] = Field(None, description="Financial news category, if any")


class ErrorResponse(BaseModel):
    """Standardized error payload returned across all API endpoints."""

    status: str = Field("error", description="Always 'error'")
    code: str = Field(..., description="Standard machine-readable error code")
    message: str = Field(..., description="Human-readable explanation of error")
    details: Optional[Any] = Field(None, description="Optional extra error context or validation errors")
