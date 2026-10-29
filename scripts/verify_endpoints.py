"""
End-to-End Live Endpoint Verification Script.
Executes representative HTTP requests against either a live running server or
an in-process HTTP TestClient to rigorously verify API behaviors.
"""

import sys
import os
import argparse
from typing import Optional, Dict, Any

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class ApiClient:
    """Unified HTTP client abstracting requests vs TestClient."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.use_live = False
        self.test_client = None

        if self.base_url:
            try:
                import requests
                resp = requests.get(f"{self.base_url}/health", timeout=1.5)
                if resp.status_code == 200:
                    self.use_live = True
                    self.requests = requests
                    print(f"[*] Connected to LIVE HTTP server at: {self.base_url}")
            except Exception:
                pass

        if not self.use_live:
            from fastapi.testclient import TestClient
            from app.main import app
            self.test_client = TestClient(app)
            print("[*] Running in IN-PROCESS TESTCLIENT mode (direct ASGI HTTP pipeline)")

    def request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
        if self.use_live:
            url = f"{self.base_url}{path}"
            return self.requests.request(method, url, json=json, params=params)
        else:
            return self.test_client.request(method, path, json=json, params=params)


def verify_endpoints(client: ApiClient) -> int:
    """Run sequential verification test suite."""
    print("=" * 70)
    print("  CAPSTONE 48: ENDPOINT VERIFICATION RUNNER")
    print("=" * 70)

    passed_count = 0
    failed_count = 0

    def assert_test(step: str, condition: bool, details: str = ""):
        nonlocal passed_count, failed_count
        if condition:
            passed_count += 1
            print(f"  [PASS] {step}")
            if details:
                print(f"         {details}")
        else:
            failed_count += 1
            print(f"  [FAIL] {step}")
            if details:
                print(f"         Error details: {details}")

    # 1. Health Probe
    resp = client.request("GET", "/health")
    assert_test(
        "GET /health returns HTTP 200 and healthy status",
        resp.status_code == 200 and resp.json().get("status") == "healthy",
        f"Status: {resp.status_code}, Body: {resp.json()}",
    )

    # 2. List Books
    resp = client.request("GET", "/api/v1/books?limit=5&offset=0")
    data = resp.json()
    assert_test(
        "GET /api/v1/books returns paginated inventory (HTTP 200)",
        resp.status_code == 200 and "items" in data and "total" in data,
        f"Total books found: {data.get('total')}, returned items: {len(data.get('items', []))}",
    )

    # 3. Create a unique book
    unique_isbn = "978-0131103627"  # The C Programming Language
    book_payload = {
        "title": "The C Programming Language (Second Edition)",
        "author": "Brian W. Kernighan, Dennis M. Ritchie",
        "isbn": unique_isbn,
        "publication_year": 1988,
        "total_copies": 3,
    }
    resp = client.request("POST", "/api/v1/books", json=book_payload)
    created_id = None
    if resp.status_code == 201:
        created_id = resp.json().get("id")
        assert_test(
            f"POST /api/v1/books creates book (HTTP 201, ID: {created_id})",
            True,
            f"Available copies: {resp.json().get('available_copies')}/{resp.json().get('total_copies')}",
        )
    elif resp.status_code == 409:
        # If already exists from earlier run, find it
        find_resp = client.request("GET", f"/api/v1/books?search=Kernighan")
        items = find_resp.json().get("items", [])
        if items:
            created_id = items[0]["id"]
            assert_test(
                f"POST /api/v1/books detected existing book (ID: {created_id})",
                True,
                "Handled idempotently",
            )
        else:
            assert_test("POST /api/v1/books create book", False, resp.text)
    else:
        assert_test("POST /api/v1/books create book", False, resp.text)

    # 4. Retrieve Created Book
    if created_id:
        resp = client.request("GET", f"/api/v1/books/{created_id}")
        assert_test(
            f"GET /api/v1/books/{created_id} retrieves resource (HTTP 200)",
            resp.status_code == 200 and resp.json().get("title") == book_payload["title"],
            f"Fetched: '{resp.json().get('title')}'",
        )

        # 5. Patch Book
        resp = client.request("PATCH", f"/api/v1/books/{created_id}", json={"total_copies": 4})
        assert_test(
            f"PATCH /api/v1/books/{created_id} updates total copies to 4 (HTTP 200)",
            resp.status_code == 200 and resp.json().get("total_copies") == 4,
            f"New total: {resp.json().get('total_copies')}, available: {resp.json().get('available_copies')}",
        )

        # 6. Borrow Book
        resp = client.request(
            "POST",
            f"/api/v1/books/{created_id}/borrow",
            json={"borrower_name": "Demo Student 001"},
        )
        borrowing_id = resp.json().get("id") if resp.status_code == 201 else None
        assert_test(
            f"POST /api/v1/books/{created_id}/borrow decrements inventory (HTTP 201)",
            resp.status_code == 201 and resp.json().get("status") == "BORROWED",
            f"Borrowing ID: {borrowing_id}",
        )

        # 7. Check Attempt to Delete with Active Borrowing (Must be 409 Conflict)
        resp = client.request("DELETE", f"/api/v1/books/{created_id}")
        assert_test(
            f"DELETE /api/v1/books/{created_id} with active borrowing yields HTTP 409 Conflict",
            resp.status_code == 409 and resp.json().get("error", {}).get("code") == "ACTIVE_BORROWINGS_EXIST",
            f"Error Code: {resp.json().get('error', {}).get('code')}",
        )

        # 8. Return Book
        resp = client.request(
            "POST",
            f"/api/v1/books/{created_id}/return",
            json={"borrowing_id": borrowing_id},
        )
        assert_test(
            f"POST /api/v1/books/{created_id}/return restores inventory (HTTP 200)",
            resp.status_code == 200 and resp.json().get("status") == "RETURNED",
            f"Borrowing status: {resp.json().get('status')}",
        )

        # 9. Clean up / Delete Book
        resp = client.request("DELETE", f"/api/v1/books/{created_id}")
        assert_test(
            f"DELETE /api/v1/books/{created_id} succeeds after return (HTTP 204 No Content)",
            resp.status_code == 204,
            "Resource cleanly removed",
        )

        # 10. Confirm 404 on Deleted Book
        resp = client.request("GET", f"/api/v1/books/{created_id}")
        assert_test(
            f"GET /api/v1/books/{created_id} on deleted book yields HTTP 404",
            resp.status_code == 404 and resp.json().get("error", {}).get("code") == "BOOK_NOT_FOUND",
            f"Formatted error message: {resp.json().get('error', {}).get('message')}",
        )

    # 11. List Borrowings
    resp = client.request("GET", "/api/v1/borrowings?limit=5")
    assert_test(
        "GET /api/v1/borrowings lists borrowing audit log (HTTP 200)",
        resp.status_code == 200 and "items" in resp.json(),
        f"Audit records recorded: {resp.json().get('total')}",
    )

    print("-" * 70)
    print(f"VERIFICATION SUMMARY: {passed_count} PASSED, {failed_count} FAILED")
    print("=" * 70)
    return 0 if failed_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Live REST API verification client.")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="FastAPI server URL")
    args = parser.parse_args()

    client = ApiClient(base_url=args.url)
    exit_code = verify_endpoints(client)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
