"""Pydantic schemas for AI simplification requests and structured responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FinancialTerm(BaseModel):
    """A financial term extracted from the article with plain-English explanation."""

    term: str = Field(..., description="Financial term or acronym (e.g., Inflation, Rate Hike, EBITDA)")
    explanation: str = Field(..., description="Clear, jargon-free explanation for beginners")


class SimplificationResult(BaseModel):
    """Structured AI simplification output."""

    simple_summary: str = Field(
        ...,
        description="2-3 sentence plain-English summary of what happened and what the article reports",
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Bullet points of the most critical facts and developments",
    )
    financial_terms: List[FinancialTerm] = Field(
        default_factory=list,
        description="List of financial terms used in the article with simplified explanations",
    )
    why_it_matters: str = Field(
        ...,
        description="Objective explanation of why this news is relevant to regular readers, consumers, or investors",
    )
    market_relevance: str = Field(
        ...,
        description="Neutral observation of how sectors, interest rates, or broader markets may be influenced without providing financial advice",
    )
    affected_groups: List[str] = Field(
        default_factory=list,
        description="Groups potentially affected (e.g., Borrowers, Tech Companies, Retail Consumers)",
    )


class SimplifyRequest(BaseModel):
    """Incoming request to simplify a single financial news article."""

    title: str = Field(..., description="Financial article title")
    description: Optional[str] = Field(None, description="Article description or excerpt")
    content: Optional[str] = Field(None, description="Full or partial article content")
    source: Optional[str] = Field("Financial News", description="News publisher or source name")
    url: Optional[str] = Field(None, description="Optional article source URL")


class ArticleSummaryMeta(BaseModel):
    """Metadata of the article being simplified in response."""

    title: str = Field(..., description="Article title")
    source: str = Field(..., description="Article source")
    url: Optional[str] = Field(None, description="Article URL")


class SimplifyResponse(BaseModel):
    """Standardized response containing the AI simplification."""

    status: str = Field("success", description="Status indicator")
    article: Dict[str, Any] = Field(..., description="Basic article metadata")
    simplification: SimplificationResult = Field(..., description="Structured AI output")


class BatchSimplifyRequest(BaseModel):
    """Incoming request to simplify multiple financial news articles."""

    articles: List[SimplifyRequest] = Field(..., min_length=1, max_length=10, description="List of articles to simplify")


class BatchSimplifyItem(BaseModel):
    """Single item in a batch simplification response."""

    article: Dict[str, Any]
    simplification: Optional[SimplificationResult] = None
    error: Optional[str] = None


class BatchSimplifyResponse(BaseModel):
    """Response containing batch simplification results."""

    status: str = Field("success", description="Status indicator")
    total_processed: int = Field(0, description="Number of articles processed")
    results: List[BatchSimplifyItem] = Field(default_factory=list, description="List of processed results")
