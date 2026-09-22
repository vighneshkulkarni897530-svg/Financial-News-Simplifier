"""Tests for Root and Health endpoints."""

from app.core.config import settings


def test_root_endpoint(client):
    """Test root GET / endpoint returns correct metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FinNews AI"
    assert data["status"] == "running"
    assert "version" in data


def test_health_endpoint(client):
    """Test health GET /health endpoint returns correct configuration health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FinNews AI"
    assert "news_api_configured" in data
    assert "groq_configured" in data
    assert data["news_api_configured"] is True
    assert data["groq_configured"] is True
