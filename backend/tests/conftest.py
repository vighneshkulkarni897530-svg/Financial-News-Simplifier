"""Shared pytest fixtures and mock test configurations."""

import os
import pytest
from fastapi.testclient import TestClient

# Set testing environment variables before importing app
os.environ["NEWS_API_KEY"] = "mock_news_api_key_12345"
os.environ["GROQ_API_KEY"] = "mock_groq_api_key_12345"
os.environ["GROQ_MODEL"] = "llama-3.3-70b-versatile"
os.environ["ENVIRONMENT"] = "testing"
os.environ["NEWS_CACHE_MINUTES"] = "5"
os.environ["MAX_ARTICLE_LENGTH"] = "12000"

from app.core.config import settings
from app.main import app
from app.services.news_service import news_service
from app.services.summarization_service import summarization_service


@pytest.fixture(autouse=True)
def clear_service_caches():
    """Clear in-memory caches before each test run."""
    news_service._cache.clear()
    summarization_service._summary_cache.clear()
    yield
    news_service._cache.clear()
    summarization_service._summary_cache.clear()


@pytest.fixture
def client():
    """FastAPI TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_newsapi_payload():
    """Sample raw payload returned by NewsAPI."""
    return {
        "status": "ok",
        "totalResults": 3,
        "articles": [
            {
                "source": {"id": "reuters", "name": "Reuters"},
                "author": "Jane Doe",
                "title": "Federal Reserve Holds Interest Rates Steady Amid Cooling Inflation",
                "description": "The Federal Reserve left its benchmark interest rate unchanged on Wednesday.",
                "url": "https://www.reuters.com/markets/us/fed-rates-steady-2026-09",
                "urlToImage": "https://www.reuters.com/images/fed-building.jpg",
                "publishedAt": "2026-09-20T14:30:00Z",
                "content": "WASHINGTON (Reuters) - The U.S. Federal Reserve held benchmark lending rates steady... [+1540 chars]",
            },
            {
                "source": {"id": "bloomberg", "name": "Bloomberg"},
                "author": "John Smith",
                "title": "Tech Stocks Surge on Semiconductor Demand and Cloud Growth",
                "description": "Major indices gained as chipmakers led a rally in technology equities.",
                "url": "https://www.bloomberg.com/news/articles/tech-surge-2026",
                "urlToImage": "https://www.bloomberg.com/images/tech-chart.jpg",
                "publishedAt": "2026-09-20T13:15:00Z",
                "content": "Technology stocks advanced sharply on strong earnings guidance... [+890 chars]",
            },
            {
                "source": {"id": None, "name": "Spam Outlet"},
                "author": None,
                "title": "[Removed]",
                "description": "[Removed]",
                "url": "https://removed.com",
                "urlToImage": None,
                "publishedAt": "2026-09-20T12:00:00Z",
                "content": "[Removed]",
            },
        ],
    }


@pytest.fixture
def sample_groq_simplification_json():
    """Sample structured JSON returned by Groq LLaMA model."""
    return {
        "simple_summary": "The Federal Reserve decided not to raise or lower interest rates because price increases in the economy are slowing down.",
        "key_points": [
            "The benchmark lending rate remains unchanged.",
            "Inflation has shown steady signs of cooling over recent months.",
            "Policymakers will wait for more economic data before making future rate changes.",
        ],
        "financial_terms": [
            {
                "term": "Benchmark Interest Rate",
                "explanation": "The baseline interest rate set by the central bank that influences what commercial banks charge consumers to borrow money.",
            },
            {
                "term": "Inflation",
                "explanation": "The gradual increase in the prices of goods and everyday services over time.",
            },
        ],
        "why_it_matters": "This means borrowing costs for things like credit cards, auto loans, and mortgages will remain steady for now rather than rising higher.",
        "market_relevance": "The article reports that markets reacted calmly as the decision met investor expectations without unexpected policy shifts.",
        "affected_groups": [
            "Homebuyers and mortgage holders",
            "Credit card users",
            "Commercial banks",
        ],
    }
