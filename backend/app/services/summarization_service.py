"""Summarization coordinator service with caching, concurrency control, and validation."""

import asyncio
import hashlib
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.summary_schema import (
    BatchSimplifyItem,
    BatchSimplifyRequest,
    BatchSimplifyResponse,
    SimplificationResult,
    SimplifyRequest,
    SimplifyResponse,
)
from app.services.groq_service import GroqServiceException, groq_service
from app.utils.text_cleaner import clean_article_text


class SummarizationServiceException(Exception):
    """Custom exception for summarization orchestration."""

    def __init__(self, code: str, message: str, status_code: int = 400, details: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class SummarizationService:
    """Orchestrates text cleaning, Groq LLM invocation, caching, and batch concurrency."""

    def __init__(self):
        # Cache simplifications: content_hash -> SimplificationResult
        self._summary_cache: Dict[str, SimplificationResult] = {}
        # Concurrency semaphore for Groq API (max 3 concurrent requests)
        self._semaphore = asyncio.Semaphore(3)

    def _hash_content(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def simplify_article(self, request: SimplifyRequest) -> SimplifyResponse:
        """Process, validate, clean, and simplify a single financial article."""
        title = (request.title or "").strip()
        if not title:
            raise SummarizationServiceException(
                code="INVALID_ARTICLE",
                message="Article title is required.",
                status_code=400,
            )

        # Clean and assemble text
        cleaned_text = clean_article_text(
            title=title,
            description=request.description,
            content=request.content,
            max_chars=settings.MAX_ARTICLE_LENGTH,
        )

        if len(cleaned_text.strip()) < 20:
            raise SummarizationServiceException(
                code="INVALID_ARTICLE",
                message="Article content is too short to provide a meaningful financial summary.",
                status_code=400,
            )

        source_name = (request.source or "Financial News").strip()
        cache_key = self._hash_content(f"{title}::{cleaned_text}")

        # Check summary cache
        if cache_key in self._summary_cache:
            logger.info(f"Returning cached summary for article: '{title[:40]}...'")
            simplification = self._summary_cache[cache_key]
        else:
            # Execute with concurrency control
            async with self._semaphore:
                simplification = await groq_service.simplify_financial_text(
                    cleaned_text=cleaned_text,
                    source=source_name,
                )
            self._summary_cache[cache_key] = simplification

        return SimplifyResponse(
            status="success",
            article={
                "title": title,
                "source": source_name,
                "url": request.url,
            },
            simplification=simplification,
        )

    async def batch_simplify(self, request: BatchSimplifyRequest) -> BatchSimplifyResponse:
        """Process multiple articles concurrently with bounded concurrency."""
        tasks = []
        for item in request.articles:
            tasks.append(self._process_single_batch_item(item))

        results = await asyncio.gather(*tasks, return_exceptions=False)
        return BatchSimplifyResponse(
            status="success",
            total_processed=len(results),
            results=results,
        )

    async def _process_single_batch_item(self, item: SimplifyRequest) -> BatchSimplifyItem:
        title = (item.title or "").strip()
        source = (item.source or "Financial News").strip()
        article_meta = {"title": title, "source": source, "url": item.url}

        try:
            res = await self.simplify_article(item)
            return BatchSimplifyItem(
                article=article_meta,
                simplification=res.simplification,
                error=None,
            )
        except (GroqServiceException, SummarizationServiceException) as err:
            logger.warning(f"Batch item failed for '{title[:30]}': {err.message}")
            return BatchSimplifyItem(
                article=article_meta,
                simplification=None,
                error=err.message,
            )
        except Exception as exc:
            logger.error(f"Unexpected error in batch item '{title[:30]}': {exc}")
            return BatchSimplifyItem(
                article=article_meta,
                simplification=None,
                error="Internal processing error occurred for this article.",
            )


# Global singleton instance
summarization_service = SummarizationService()
