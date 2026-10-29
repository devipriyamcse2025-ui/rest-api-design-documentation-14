"""
Automated unit and integration tests for Book endpoints.
Tests CRUD operations, pagination, search, validation, and error scenarios.
"""

from fastapi.testclient import TestClient
from app.models import Book


def test_create_book_success(client: TestClient):
    """POST /api/v1/books creates a book and initializes copies."""
    payload = {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "isbn": "978-0134494166",
        "publication_year": 2017,
        "total_copies": 5,
    }
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == payload["title"]
    assert data["isbn"] == payload["isbn"]
    assert data["total_copies"] == 5
    assert data["available_copies"] == 5
    assert "created_at" in data
    assert "updated_at" in data


def test_create_book_duplicate_isbn_yields_409(client: TestClient, sample_book: Book):
    """POST /api/v1/books with existing ISBN must return 409 Conflict."""
    payload = {
        "title": "Duplicate Book Entry",
        "author": "Another Author",
        "isbn": sample_book.isbn,
        "publication_year": 2020,
        "total_copies": 2,
    }
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "DUPLICATE_ISBN"
    assert "already exists" in data["error"]["message"]


def test_list_books_and_pagination(client: TestClient, sample_book: Book):
    """GET /api/v1/books returns paginated inventory."""
    response = client.get("/api/v1/books?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert any(b["id"] == sample_book.id for b in data["items"])


def test_search_books_by_title_and_author(client: TestClient, sample_book: Book):
    """GET /api/v1/books?search=... searches by title and author case-insensitively."""
    # Search by author substring
    response = client.get("/api/v1/books?search=Beck")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["author"] == "Kent Beck"

    # Search by title substring
    response = client.get("/api/v1/books?search=driven")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    # Search with no match
    response = client.get("/api/v1/books?search=NonExistentQueryXYZ")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_book_by_id_success(client: TestClient, sample_book: Book):
    """GET /api/v1/books/{id} retrieves an existing book."""
    response = client.get(f"/api/v1/books/{sample_book.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_book.id
    assert data["title"] == sample_book.title


def test_get_book_not_found_yields_404(client: TestClient):
    """GET /api/v1/books/{id} returns 404 for nonexistent ID."""
    response = client.get("/api/v1/books/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "BOOK_NOT_FOUND"


def test_replace_book_put_success(client: TestClient, sample_book: Book):
    """PUT /api/v1/books/{id} replaces entire book."""
    payload = {
        "title": "TDD by Example - Revised",
        "author": "Kent Beck",
        "isbn": sample_book.isbn,
        "publication_year": 2003,
        "total_copies": 6,
    }
    response = client.put(f"/api/v1/books/{sample_book.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "TDD by Example - Revised"
    assert data["total_copies"] == 6
    assert data["available_copies"] == 6


def test_patch_book_partial_update(client: TestClient, sample_book: Book):
    """PATCH /api/v1/books/{id} updates only provided fields."""
    response = client.patch(f"/api/v1/books/{sample_book.id}", json={"title": "Updated Title Only"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title Only"
    assert data["author"] == sample_book.author  # Unchanged


def test_delete_book_success(client: TestClient, sample_book: Book):
    """DELETE /api/v1/books/{id} deletes book and returns 204."""
    response = client.delete(f"/api/v1/books/{sample_book.id}")
    assert response.status_code == 204
    assert response.text == ""

    # Verify book is gone
    get_resp = client.get(f"/api/v1/books/{sample_book.id}")
    assert get_resp.status_code == 404


def test_validation_errors_on_invalid_fields(client: TestClient):
    """Invalid publication year and invalid copies must return 422 with standard format."""
    # Future publication year
    future_year = 2099
    payload = {
        "title": "Future Book",
        "author": "Time Traveler",
        "isbn": "978-0131103627",
        "publication_year": future_year,
        "total_copies": 2,
    }
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

    # Negative copies
    payload["publication_year"] = 2020
    payload["total_copies"] = 0
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
