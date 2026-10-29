"""
Automated tests for unified error formatting, edge cases, and OpenAPI consistency.
"""

from fastapi.testclient import TestClient
from app.main import app


def test_404_error_envelope_structure(client: TestClient):
    """Ensure 404 responses conform to the standard error envelope."""
    response = client.get("/api/v1/books/999999")
    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "BOOK_NOT_FOUND"


def test_422_validation_error_envelope_structure(client: TestClient):
    """Ensure 422 validation errors conform to the standard error envelope."""
    # Sending string to integer path param
    response = client.get("/api/v1/books/invalid-id-string")
    assert response.status_code == 422
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]
    assert isinstance(data["error"]["details"], list)
    assert len(data["error"]["details"]) > 0


def test_openapi_schema_contains_all_core_routes():
    """Verify that the FastAPI OpenAPI generator documents all required paths."""
    schema = app.openapi()
    assert "paths" in schema
    paths = schema["paths"]

    expected_routes = [
        "/health",
        "/api/v1/books",
        "/api/v1/books/{book_id}",
        "/api/v1/books/{book_id}/borrow",
        "/api/v1/books/{book_id}/return",
        "/api/v1/borrowings",
    ]

    for route in expected_routes:
        assert route in paths, f"Route '{route}' missing from OpenAPI specification."


def test_database_isolation_between_tests(client: TestClient):
    """Verify that test fixtures clean up properly and do not leak between test runs."""
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    # In an isolated run without sample_book fixture, items should be empty
    assert response.json()["total"] == 0
