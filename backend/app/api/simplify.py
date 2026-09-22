"""AI Simplification API endpoints for financial articles."""

from fastapi import APIRouter, HTTPException
from app.schemas.summary_schema import (
    BatchSimplifyRequest,
    BatchSimplifyResponse,
    SimplifyRequest,
    SimplifyResponse,
)
from app.services.groq_service import GroqServiceException
from app.services.summarization_service import (
    SummarizationServiceException,
    summarization_service,
)

router = APIRouter(prefix="/api/simplify", tags=["AI Simplification"])


@router.post(
    "",
    summary="Simplify Financial Article",
    description="Transforms a complex financial article into a structured, jargon-free summary using Groq's LLaMA 3.3 70B model.",
    response_model=SimplifyResponse,
)
async def simplify_article_endpoint(request: SimplifyRequest) -> SimplifyResponse:
    """Simplify a single financial article."""
    try:
        return await summarization_service.simplify_article(request)
    except (GroqServiceException, SummarizationServiceException) as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post(
    "/batch",
    summary="Batch Simplify Financial Articles",
    description="Processes up to 10 articles concurrently with rate-limiting protection.",
    response_model=BatchSimplifyResponse,
)
async def batch_simplify_endpoint(request: BatchSimplifyRequest) -> BatchSimplifyResponse:
    """Batch simplify multiple financial articles."""
    try:
        return await summarization_service.batch_simplify(request)
    except (GroqServiceException, SummarizationServiceException) as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )
