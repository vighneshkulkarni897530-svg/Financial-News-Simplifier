"""Text cleaning, HTML sanitization, and content truncation utilities."""

import html
import re
from typing import Optional


def clean_html(raw_html: Optional[str]) -> str:
    """Remove HTML tags, script/style blocks, and decode entities."""
    if not raw_html:
        return ""

    # Remove script and style elements
    cleaned = re.sub(r"<(script|style).*?>.*?</\1>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    cleaned = re.sub(r"<[^<]+?>", " ", cleaned)
    # Decode HTML entities
    cleaned = html.unescape(cleaned)
    # Strip zero-width and control characters
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
    return normalize_whitespace(cleaned)


def normalize_whitespace(text: Optional[str]) -> str:
    """Normalize irregular whitespace, tabs, and duplicate blank lines."""
    if not text:
        return ""
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ").replace("\u200b", "")
    # Normalize multiple horizontal spaces to single space
    text = re.sub(r"[ \t]+", " ", text)
    # Normalize 3+ newlines to 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 12000) -> str:
    """Cleanly truncate text to max_chars without chopping mid-sentence if possible."""
    if not text or len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    # Try to find last sentence boundary (. ! ? \n)
    last_punct = max(
        truncated.rfind(". "),
        truncated.rfind("! "),
        truncated.rfind("? "),
        truncated.rfind("\n"),
    )

    if last_punct > max_chars * 0.7:
        return truncated[: last_punct + 1].strip()

    # Fallback to word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.7:
        return truncated[:last_space].strip() + "..."

    return truncated.strip() + "..."


def clean_article_text(
    title: str,
    description: Optional[str] = None,
    content: Optional[str] = None,
    max_chars: int = 12000,
) -> str:
    """Combine, sanitize, and truncate article fields for LLM processing."""
    parts = []

    clean_title = clean_html(title)
    if clean_title:
        parts.append(f"Title: {clean_title}")

    clean_desc = clean_html(description)
    if clean_desc and clean_desc.lower() not in clean_title.lower():
        parts.append(f"Summary / Excerpt: {clean_desc}")

    clean_body = clean_html(content)
    # NewsAPI often appends '[+1234 chars]' to content, remove that artifact
    if clean_body:
        clean_body = re.sub(r"\[\+\d+\s*chars\]", "", clean_body).strip()
        if clean_body and clean_body.lower() not in (clean_desc or "").lower():
            parts.append(f"Content: {clean_body}")

    combined = "\n\n".join(parts)
    return truncate_text(combined, max_chars=max_chars)


def normalize_title_for_dedup(title: Optional[str], source: Optional[str] = None) -> str:
    """Create normalized lower-case key for deduplication."""
    t = (title or "").lower()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()

    s = (source or "").lower()
    s = re.sub(r"[^\w\s]", "", s).strip()

    return f"{t}::{s}"
