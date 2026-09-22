"""Groq AI Service integrating LLaMA 3.3 70B for structured financial news simplification."""

import json
import re
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.summary_schema import SimplificationResult
from app.utils.prompts import MASTER_SYSTEM_PROMPT, build_simplification_prompt


class GroqServiceException(Exception):
    """Custom exception for Groq AI operations."""

    def __init__(self, code: str, message: str, status_code: int = 500, details: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class GroqService:
    """Async service communicating with Groq API for LLaMA 3.3 70B inference."""

    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def _extract_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Extract and parse JSON object from model response safely."""
        text = raw_text.strip()
        # Remove markdown fences if present
        if "```json" in text:
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()
        elif "```" in text:
            match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()

        # Find first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace : last_brace + 1]

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse LLM JSON response: {exc}. Raw text: {raw_text[:500]}")
            raise GroqServiceException(
                code="AI_RESPONSE_ERROR",
                message="AI model produced malformed output. Please retry.",
                status_code=502,
                details={"raw_snippet": raw_text[:200]},
            )

    async def simplify_financial_text(
        self,
        cleaned_text: str,
        source: str = "Financial Source",
        category_hint: str = "General Finance",
    ) -> SimplificationResult:
        """Call Groq LLaMA 3.3 70B to generate structured simplification."""
        if not settings.is_groq_configured:
            logger.error("GROQ_API_KEY is not configured in settings")
            raise GroqServiceException(
                code="MISSING_CONFIGURATION",
                message="Groq API key is not configured. Please set GROQ_API_KEY in your .env file.",
                status_code=503,
            )

        user_prompt = build_simplification_prompt(
            article_text=cleaned_text,
            source=source,
            category_hint=category_hint,
        )

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 1500,
        }

        models_to_try = [settings.GROQ_MODEL]
        fallback_models = ["openai/gpt-oss-120b", "groq/compound", "qwen/qwen3.8-27b", "groq/compound-mini"]
        for fm in fallback_models:
            if fm not in models_to_try:
                models_to_try.append(fm)

        last_error_text = ""
        response = None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for model_candidate in models_to_try:
                    payload["model"] = model_candidate
                    logger.info(f"Sending request to Groq model: {model_candidate} (input chars: {len(cleaned_text)})")
                    response = await client.post(self.api_url, headers=headers, json=payload)

                    if response.status_code == 200:
                        break
                    elif response.status_code == 404:
                        logger.warning(f"Model '{model_candidate}' returned 404. Trying next available model...")
                        last_error_text = response.text
                        continue
                    elif response.status_code in (401, 403):
                        logger.error(f"Groq API authentication failed: {response.status_code}")
                        raise GroqServiceException(
                            code="GROQ_API_ERROR",
                            message="Invalid or unauthorized Groq API key. Please verify GROQ_API_KEY.",
                            status_code=401,
                        )
                    elif response.status_code == 429:
                        logger.warning("Groq API rate limit reached")
                        raise GroqServiceException(
                            code="GROQ_API_RATE_LIMIT",
                            message="Groq AI rate limit exceeded. Please wait a moment before requesting another summary.",
                            status_code=429,
                        )
                    else:
                        last_error_text = response.text

            if response is None or response.status_code != 200:
                logger.error(f"All Groq model attempts failed. Last status: {response.status_code if response else 'None'}, text: {last_error_text}")
                raise GroqServiceException(
                    code="GROQ_API_ERROR",
                    message=f"Groq API returned error: {last_error_text[:200] if last_error_text else 'Unknown error'}",
                    status_code=502,
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise GroqServiceException(
                    code="AI_RESPONSE_ERROR",
                    message="Groq returned an empty choice response.",
                    status_code=502,
                )

            raw_content = choices[0].get("message", {}).get("content", "")
            if not raw_content:
                raise GroqServiceException(
                    code="AI_RESPONSE_ERROR",
                    message="Groq returned empty message content.",
                    status_code=502,
                )

            parsed_data = self._extract_and_parse_json(raw_content)

            # Validate structured model with Pydantic
            try:
                # Ensure fields exist with safe fallbacks if slightly altered
                simple_summary = parsed_data.get("simple_summary") or "Summary not available."
                key_points = parsed_data.get("key_points") or []
                financial_terms = parsed_data.get("financial_terms") or []
                why_it_matters = parsed_data.get("why_it_matters") or "No relevance context provided."
                market_relevance = parsed_data.get("market_relevance") or "No market context provided."
                affected_groups = parsed_data.get("affected_groups") or []

                return SimplificationResult(
                    simple_summary=str(simple_summary),
                    key_points=[str(p) for p in key_points if p],
                    financial_terms=financial_terms,
                    why_it_matters=str(why_it_matters),
                    market_relevance=str(market_relevance),
                    affected_groups=[str(g) for g in affected_groups if g],
                )
            except Exception as val_err:
                logger.error(f"Pydantic validation of LLM output failed: {val_err}")
                raise GroqServiceException(
                    code="AI_RESPONSE_ERROR",
                    message=f"Failed to validate AI response format: {str(val_err)}",
                    status_code=502,
                )

        except httpx.TimeoutException:
            logger.error("Groq API request timed out after 30s")
            raise GroqServiceException(
                code="GROQ_API_TIMEOUT",
                message="AI analysis timed out. Groq service took too long to respond.",
                status_code=504,
            )
        except httpx.RequestError as exc:
            logger.error(f"Groq API connection error: {exc}")
            raise GroqServiceException(
                code="GROQ_API_ERROR",
                message=f"Failed to communicate with Groq AI service: {str(exc)}",
                status_code=502,
            )


# Global singleton instance
groq_service = GroqService()
