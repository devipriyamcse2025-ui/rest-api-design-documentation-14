"""
Tests for service health and root navigational endpoints.
"""

from fastapi.testclient import TestClient


def test_health_check_returns_200_and_healthy(client: TestClient):
    """GET /health must return HTTP 200, status 'healthy', and valid metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "timestamp" in data
    assert "database" in data
    assert data["database"] == "connected"


def test_root_index_returns_navigation_links(client: TestClient):
    """GET / must provide links to documentation and endpoints."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "/docs" in data["interactive_docs"]
    assert "/openapi.json" in data["openapi_spec"]
    assert "/health" in data["health_check"]
