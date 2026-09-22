"""Utilities package for FinNews AI."""

from app.utils.prompts import (
    BUSINESS_NEWS_PROMPT,
    ECONOMIC_NEWS_PROMPT,
    MARKET_EVENT_PROMPT,
    MASTER_SYSTEM_PROMPT,
    TERMINOLOGY_PROMPT,
    build_simplification_prompt,
)
from app.utils.text_cleaner import (
    clean_article_text,
    clean_html,
    normalize_title_for_dedup,
    normalize_whitespace,
    truncate_text,
)

__all__ = [
    "clean_html",
    "normalize_whitespace",
    "truncate_text",
    "clean_article_text",
    "normalize_title_for_dedup",
    "MASTER_SYSTEM_PROMPT",
    "build_simplification_prompt",
    "MARKET_EVENT_PROMPT",
    "ECONOMIC_NEWS_PROMPT",
    "BUSINESS_NEWS_PROMPT",
    "TERMINOLOGY_PROMPT",
]
