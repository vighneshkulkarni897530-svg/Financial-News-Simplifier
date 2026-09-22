"""Unit and integration tests for financial news retrieval, caching, and deduplication."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest

from app.core.config import settings
from app.services.news_service import news_service


def test_get_news_success(client, sample_newsapi_payload):
    """Test successful news retrieval with normalized response."""
    mock_resp = httpx.Response(200, json=sample_newsapi_payload, request=httpx.Request("GET", "https://newsapi.org"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        response = client.get("/api/news?category=markets")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # 3 items in sample, 1 is [Removed], so 2 valid articles
        assert data["total_results"] == 2
        assert len(data["articles"]) == 2

        article1 = data["articles"][0]
        assert article1["title"] == "Federal Reserve Holds Interest Rates Steady Amid Cooling Inflation"
        assert article1["source"] == "Reuters"
        assert article1["url"] == "https://www.reuters.com/markets/us/fed-rates-steady-2026-09"
        assert article1["image_url"] == "https://www.reuters.com/images/fed-building.jpg"


def test_news_search_endpoint(client, sample_newsapi_payload):
    """Test search endpoint /api/news/search."""
    mock_resp = httpx.Response(200, json=sample_newsapi_payload, request=httpx.Request("GET", "https://newsapi.org"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        response = client.get("/api/news/search?query=inflation")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["query"] == "inflation"


def test_news_in_memory_caching(client, sample_newsapi_payload):
    """Test that second call with same params hits in-memory cache without extra HTTP call."""
    mock_resp = httpx.Response(200, json=sample_newsapi_payload, request=httpx.Request("GET", "https://newsapi.org"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        # First request - should call NewsAPI
        res1 = client.get("/api/news?category=business")
        assert res1.status_code == 200
        assert mock_get.call_count == 1

        # Second request with identical params - should hit cache
        res2 = client.get("/api/news?category=business")
        assert res2.status_code == 200
        assert mock_get.call_count == 1  # Still 1, cache hit!


def test_news_deduplication():
    """Test deduplication logic in news service normalization."""
    duplicate_payload = [
        {
            "source": {"name": "Wall Street Journal"},
            "title": "Inflation Drops to 2.1 Percent",
            "url": "https://wsj.com/inflation-1",
            "content": "Article content 1",
        },
        {
            "source": {"name": "Wall Street Journal"},
            "title": "Inflation Drops to 2.1 Percent",
            "url": "https://wsj.com/inflation-1",  # duplicate URL
            "content": "Article content 1 duplicate",
        },
        {
            "source": {"name": "Wall Street Journal"},
            "title": "Inflation Drops to 2.1 Percent!",  # duplicate title + source
            "url": "https://wsj.com/inflation-syndicated",
            "content": "Syndicated copy",
        },
    ]

    normalized = news_service._normalize_and_filter_articles(duplicate_payload)
    assert len(normalized) == 1
    assert normalized[0].title == "Inflation Drops to 2.1 Percent"


def test_news_rate_limit_error(client):
    """Test handling 429 Rate Limit from NewsAPI."""
    mock_resp = httpx.Response(429, json={"status": "error", "message": "rateLimited"}, request=httpx.Request("GET", "https://newsapi.org"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        response = client.get("/api/news")
        assert response.status_code == 429
        data = response.json()
        assert data["status"] == "error"
        assert data["code"] == "NEWS_API_RATE_LIMIT"


def test_news_timeout_error(client):
    """Test handling timeout from NewsAPI."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Connection timed out")

        response = client.get("/api/news")
        assert response.status_code == 504
        data = response.json()
        assert data["status"] == "error"
        assert data["code"] == "NEWS_API_TIMEOUT"


def test_news_missing_api_key(client, monkeypatch):
    """Test missing NewsAPI key raises MISSING_CONFIGURATION error."""
    monkeypatch.setattr(settings, "NEWS_API_KEY", "")

    response = client.get("/api/news")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "MISSING_CONFIGURATION"
