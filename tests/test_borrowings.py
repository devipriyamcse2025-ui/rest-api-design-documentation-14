"""
Automated tests for borrowing workflow and inventory safety.
Tests borrowing, returning, concurrency/exhaustion constraints, and deletion policies.
"""

from fastapi.testclient import TestClient
from app.models import Book


def test_borrow_available_book_success(client: TestClient, sample_book: Book):
    """Borrowing an available book decrements available copies and creates record."""
    initial_available = sample_book.available_copies
    payload = {"borrower_name": "Demo Student Alice"}

    response = client.post(f"/api/v1/books/{sample_book.id}/borrow", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["book_id"] == sample_book.id
    assert data["borrower_name"] == "Demo Student Alice"
    assert data["status"] == "BORROWED"
    assert data["returned_at"] is None

    # Verify inventory was decremented
    book_resp = client.get(f"/api/v1/books/{sample_book.id}")
    assert book_resp.json()["available_copies"] == initial_available - 1


def test_borrow_exhausts_copies_and_rejects_further_borrows(client: TestClient):
    """Borrowing when available_copies == 0 yields 409 Conflict."""
    # Create single copy book
    book_payload = {
        "title": "Rare Limited Edition",
        "author": "Rare Author",
        "isbn": "978-0201633610",
        "publication_year": 1994,
        "total_copies": 1,
    }
    create_resp = client.post("/api/v1/books", json=book_payload)
    book_id = create_resp.json()["id"]

    # First borrow succeeds
    resp1 = client.post(f"/api/v1/books/{book_id}/borrow")
    assert resp1.status_code == 201

    # Second borrow must fail with 409 Conflict
    resp2 = client.post(f"/api/v1/books/{book_id}/borrow")
    assert resp2.status_code == 409
    data = resp2.json()
    assert data["error"]["code"] == "NO_COPIES_AVAILABLE"
    assert "No copies" in data["error"]["message"]


def test_return_book_restores_inventory(client: TestClient, sample_book: Book):
    """Returning a borrowed book restores available copies."""
    # Borrow first
    borrow_resp = client.post(f"/api/v1/books/{sample_book.id}/borrow")
    assert borrow_resp.status_code == 201
    borrowing_id = borrow_resp.json()["id"]

    # Now return
    return_resp = client.post(f"/api/v1/books/{sample_book.id}/return", json={"borrowing_id": borrowing_id})
    assert return_resp.status_code == 200
    data = return_resp.json()
    assert data["status"] == "RETURNED"
    assert data["returned_at"] is not None

    # Verify inventory is restored
    book_resp = client.get(f"/api/v1/books/{sample_book.id}")
    assert book_resp.json()["available_copies"] == sample_book.total_copies


def test_return_when_no_active_borrowing_yields_404(client: TestClient, sample_book: Book):
    """Attempting to return a book with no active borrowings returns 404."""
    response = client.post(f"/api/v1/books/{sample_book.id}/return")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NO_ACTIVE_BORROWING"


def test_cannot_delete_book_with_active_borrowing(client: TestClient, sample_book: Book):
    """Deleting a book with active unreturned borrowings must be rejected with 409 Conflict."""
    # Borrow a copy
    client.post(f"/api/v1/books/{sample_book.id}/borrow")

    # Try to delete
    delete_resp = client.delete(f"/api/v1/books/{sample_book.id}")
    assert delete_resp.status_code == 409
    data = delete_resp.json()
    assert data["error"]["code"] == "ACTIVE_BORROWINGS_EXIST"
    assert "active borrowing records" in data["error"]["message"]

    # Book still exists
    get_resp = client.get(f"/api/v1/books/{sample_book.id}")
    assert get_resp.status_code == 200


def test_list_borrowings_pagination_and_filtering(client: TestClient, sample_book: Book):
    """GET /api/v1/borrowings returns paginated records with optional filters."""
    # Perform borrow and return
    b_resp = client.post(f"/api/v1/books/{sample_book.id}/borrow")
    borrowing_id = b_resp.json()["id"]
    client.post(f"/api/v1/books/{sample_book.id}/return", json={"borrowing_id": borrowing_id})

    # Query all borrowings
    resp = client.get("/api/v1/borrowings?limit=10&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert "items" in data

    # Filter by status RETURNED
    resp_returned = client.get("/api/v1/borrowings?status=RETURNED")
    assert resp_returned.status_code == 200
    assert all(item["status"] == "RETURNED" for item in resp_returned.json()["items"])

    # Filter by book_id
    resp_book = client.get(f"/api/v1/borrowings?book_id={sample_book.id}")
    assert resp_book.status_code == 200
    assert all(item["book_id"] == sample_book.id for item in resp_book.json()["items"])
