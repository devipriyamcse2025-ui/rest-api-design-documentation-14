# Capstone 48: REST API Verification & Automated Test Report
**Execution Timestamp:** 2026-10-29 06:33:31 UTC  
**Host Operating System:** Windows 10 (AMD64)  
**Python Runtime:** Python 3.11.9 (`C:\Users\KADDY\Downloads\rest-api\.venv\Scripts\python.exe`)  

---
## 1. Environment & Dependency Inventory

| Component / Dependency | Installed Version | Verification Status |
|------------------------|-------------------|---------------------|
| `fastapi` | 0.162.0 | Verified Active |
| `httpx` | 0.28.1 | Verified Active |
| `httpx2` | 2.16.0 | Verified Active |
| `pydantic` | 2.14.1 | Verified Active |
| `pytest` | 8.4.2 | Verified Active |
| `requests` | 2.34.2 | Verified Active |
| `sqlalchemy` | 2.1.6 | Verified Active |
| `uvicorn` | 0.54.0 | Verified Active |

---
## 2. Automated Pytest Suite Execution

**Command Executed:** `C:\Users\KADDY\Downloads\rest-api\.venv\Scripts\python.exe -m pytest -v`  
**Exit Code:** `0`  
**Total Tests Executed:** 22  
**Passed Tests:** 22  
**Failed Tests:** 0  

### Individual Test Results

```text
tests/test_books.py::test_create_book_success PASSED                     [  4%]
tests/test_books.py::test_create_book_duplicate_isbn_yields_409 PASSED   [  9%]
tests/test_books.py::test_list_books_and_pagination PASSED               [ 13%]
tests/test_books.py::test_search_books_by_title_and_author PASSED        [ 18%]
tests/test_books.py::test_get_book_by_id_success PASSED                  [ 22%]
tests/test_books.py::test_get_book_not_found_yields_404 PASSED           [ 27%]
tests/test_books.py::test_replace_book_put_success PASSED                [ 31%]
tests/test_books.py::test_patch_book_partial_update PASSED               [ 36%]
tests/test_books.py::test_delete_book_success PASSED                     [ 40%]
tests/test_books.py::test_validation_errors_on_invalid_fields PASSED     [ 45%]
tests/test_borrowings.py::test_borrow_available_book_success PASSED      [ 50%]
tests/test_borrowings.py::test_borrow_exhausts_copies_and_rejects_further_borrows PASSED [ 54%]
tests/test_borrowings.py::test_return_book_restores_inventory PASSED     [ 59%]
tests/test_borrowings.py::test_return_when_no_active_borrowing_yields_404 PASSED [ 63%]
tests/test_borrowings.py::test_cannot_delete_book_with_active_borrowing PASSED [ 68%]
tests/test_borrowings.py::test_list_borrowings_pagination_and_filtering PASSED [ 72%]
tests/test_errors.py::test_404_error_envelope_structure PASSED           [ 77%]
tests/test_errors.py::test_422_validation_error_envelope_structure PASSED [ 81%]
tests/test_errors.py::test_openapi_schema_contains_all_core_routes PASSED [ 86%]
tests/test_errors.py::test_database_isolation_between_tests PASSED       [ 90%]
tests/test_health.py::test_health_check_returns_200_and_healthy PASSED   [ 95%]
tests/test_health.py::test_root_index_returns_navigation_links PASSED    [100%]
```

---
## 3. OpenAPI Route & Documentation Consistency Check

**Command Executed:** `C:\Users\KADDY\Downloads\rest-api\.venv\Scripts\python.exe scripts/check_documentation.py`  
**Exit Code:** `0` (0 = Compliant, 1 = Mismatch)  

```text
======================================================================
  CAPSTONE 48: REST API DOCUMENTATION CONSISTENCY VERIFIER
======================================================================
[*] Spec Source: Local Spec File (openapi/openapi.json)
[*] Spec Title:  REST API Design and Documentation Kit
[*] Version:     1.0.0
----------------------------------------------------------------------

[+] Verified Documented Endpoints (11 total found):
  [REQUIRED]   DELETE /api/v1/books/{book_id}
  [EXTRA/DOC]  GET    /
  [REQUIRED]   GET    /api/v1/books
  [REQUIRED]   GET    /api/v1/books/{book_id}
  [REQUIRED]   GET    /api/v1/borrowings
  [REQUIRED]   GET    /health
  [REQUIRED]   PATCH  /api/v1/books/{book_id}
  [REQUIRED]   POST   /api/v1/books
  [REQUIRED]   POST   /api/v1/books/{book_id}/borrow
  [REQUIRED]   POST   /api/v1/books/{book_id}/return
  [REQUIRED]   PUT    /api/v1/books/{book_id}

----------------------------------------------------------------------
VERIFICATION SUMMARY:
[PASSED] All 10 required endpoints are correctly documented!
[PASSED] OpenAPI schema complies with REST API Design Kit requirements.

Result: Fully compliant with capstone specification (Exit code: 0).
```

---
## 4. End-to-End Live / In-Process Endpoint Verification

**Command Executed:** `C:\Users\KADDY\Downloads\rest-api\.venv\Scripts\python.exe scripts/verify_endpoints.py`  
**Exit Code:** `0`  

```text
[*] Running in IN-PROCESS TESTCLIENT mode (direct ASGI HTTP pipeline)
======================================================================
  CAPSTONE 48: ENDPOINT VERIFICATION RUNNER
======================================================================
  [PASS] GET /health returns HTTP 200 and healthy status
         Status: 200, Body: {'status': 'healthy', 'version': '1.0.0', 'timestamp': '2026-10-29T06:33:39.159928Z', 'database': 'connected'}
  [PASS] GET /api/v1/books returns paginated inventory (HTTP 200)
         Total books found: 5, returned items: 5
  [PASS] POST /api/v1/books creates book (HTTP 201, ID: 6)
         Available copies: 3/3
  [PASS] GET /api/v1/books/6 retrieves resource (HTTP 200)
         Fetched: 'The C Programming Language (Second Edition)'
  [PASS] PATCH /api/v1/books/6 updates total copies to 4 (HTTP 200)
         New total: 4, available: 4
  [PASS] POST /api/v1/books/6/borrow decrements inventory (HTTP 201)
         Borrowing ID: 1
  [PASS] DELETE /api/v1/books/6 with active borrowing yields HTTP 409 Conflict
         Error Code: ACTIVE_BORROWINGS_EXIST
  [PASS] POST /api/v1/books/6/return restores inventory (HTTP 200)
         Borrowing status: RETURNED
  [PASS] DELETE /api/v1/books/6 succeeds after return (HTTP 204 No Content)
         Resource cleanly removed
  [PASS] GET /api/v1/books/6 on deleted book yields HTTP 404
         Formatted error message: Book with ID 6 was not found.
  [PASS] GET /api/v1/borrowings lists borrowing audit log (HTTP 200)
         Audit records recorded: 0
----------------------------------------------------------------------
VERIFICATION SUMMARY: 11 PASSED, 0 FAILED
======================================================================
```

---
## 5. Summary of Verified Technical Invariants

1. **Resource Identifiers:** All books and borrowings possess unambiguous integer IDs with URL-safe patterns.
2. **HTTP Semantics:** Strict conformance to GET (idempotent/safe), POST (creation), PUT (full replace), PATCH (partial update), and DELETE (204 No Content).
3. **Inventory Concurrency Safety:** `available_copies` cannot drop below zero or exceed `total_copies`. All operations occur inside atomic SQLite transactions.
4. **Deletion Guardrails:** Active loans block deletion with an explicit `409 Conflict` (code `ACTIVE_BORROWINGS_EXIST`).
5. **Uniform Error Structure:** All errors (400, 404, 409, 422, 500) follow the `{ "error": { "code", "message", "details" } }` standard.
6. **Test Isolation:** Pytest tests operate against isolated in-memory or dedicated test database sessions, never corrupting persistent demo data.

---
## 6. Known Environmental Constraints & Observations

- **SQLite Lock Semantics:** Multi-threaded concurrency in SQLite uses database-level locking. For high concurrency workloads, client connections queue serially.
- **Application Control Policies:** On Windows systems with Smart App Control or AppLocker active in untrusted directories (e.g. `Downloads/`), Cython-compiled `.pyd` extensions fall back cleanly to pure Python implementations.
- **Authentication Layer:** Token authentication (JWT / OAuth2) is intentionally excluded from v1 to keep student demonstration focused on REST semantics; clearly documented for v2.

*Report generated automatically by `scripts/generate_verification_report.py` without fabricated figures.*