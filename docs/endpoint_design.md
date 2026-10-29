# REST API Endpoint Design Specification
**Project:** REST API Design and Documentation Kit (Capstone 48)  
**Version:** 1.0.0  
**Base URL:** `http://127.0.0.1:8000`  
**Content-Type:** `application/json`  

---

## 1. Architectural Overview & Parameter Taxonomy
This API follows standard REST principles where URLs represent resources and HTTP verbs indicate actions. Requests and responses interact using four categories of parameters:
1. **Path Parameters:** Embedded in the URL path (e.g. `{book_id}`) to target a specific resource entity uniquely.
2. **Query Parameters:** Appended after `?` (e.g. `?limit=10&search=clean`) to filter, paginate, or sort collections without changing the resource identity.
3. **Request Body:** JSON-formatted data sent via `POST`, `PUT`, or `PATCH` containing the representation or mutation details.
4. **Response Models:** JSON objects returned with matching HTTP status codes.

---

## 2. Master Endpoint Inventory Table

| HTTP Method | Endpoint URI | Purpose / Action | Required Parameters | Request Body | Success Status | Error Statuses |
|-------------|--------------|------------------|---------------------|--------------|----------------|----------------|
| `GET` | `/health` | Service health & database connectivity probe | None | None | `200 OK` | `500` |
| `GET` | `/` | Root index with interactive documentation links | None | None | `200 OK` | `500` |
| `GET` | `/api/v1/books` | List books with pagination & substring search | None (Optional: `limit`, `offset`, `search`) | None | `200 OK` | `422, 500` |
| `GET` | `/api/v1/books/{book_id}` | Retrieve single book details by ID | Path: `book_id` (int >= 1) | None | `200 OK` | `404, 422, 500` |
| `POST` | `/api/v1/books` | Create a new book in inventory | None | JSON `BookCreate` | `201 Created` | `409, 422, 500` |
| `PUT` | `/api/v1/books/{book_id}` | Completely replace an existing book | Path: `book_id` (int >= 1) | JSON `BookUpdate` | `200 OK` | `400, 404, 409, 422, 500` |
| `PATCH` | `/api/v1/books/{book_id}` | Partially update fields of an existing book | Path: `book_id` (int >= 1) | JSON `BookPatch` | `200 OK` | `400, 404, 409, 422, 500` |
| `DELETE` | `/api/v1/books/{book_id}` | Permanently delete a book (if no active loans) | Path: `book_id` (int >= 1) | None | `204 No Content` | `404, 409, 422, 500` |
| `POST` | `/api/v1/books/{book_id}/borrow` | Borrow an available copy of a book | Path: `book_id` (int >= 1) | Optional: `BorrowRequest` | `201 Created` | `404, 409, 422, 500` |
| `POST` | `/api/v1/books/{book_id}/return` | Return a borrowed copy of a book | Path: `book_id` (int >= 1) | Optional: `ReturnRequest` | `200 OK` | `400, 404, 422, 500` |
| `GET` | `/api/v1/borrowings` | List borrowing audit records with filters | None (Optional: `limit`, `offset`, `status`, `book_id`) | None | `200 OK` | `422, 500` |

---

## 3. Detailed Endpoint Specifications & Realistic Examples

### 3.1 Health Check Probe
- **Method & Path:** `GET /health`
- **Description:** Cloud-native health probe reporting runtime operational status and database reachability.
- **Example Request:**
  ```http
  GET /health HTTP/1.1
  Host: 127.0.0.1:8000
  Accept: application/json
  ```
- **Example Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2026-10-29T12:00:00.000000Z",
    "database": "connected"
  }
  ```

---

### 3.2 List Books
- **Method & Path:** `GET /api/v1/books`
- **Query Parameters:**
  - `limit` (integer, optional, default: 10, min: 1, max: 100): Maximum records per page.
  - `offset` (integer, optional, default: 0, min: 0): Records to skip from beginning.
  - `search` (string, optional, min_length: 1, max_length: 100): Case-insensitive match on title or author.
- **Example Request:**
  ```http
  GET /api/v1/books?limit=2&offset=0&search=design HTTP/1.1
  Host: 127.0.0.1:8000
  ```
- **Example Response (200 OK):**
  ```json
  {
    "items": [
      {
        "id": 2,
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "isbn": "978-1449373320",
        "publication_year": 2017,
        "total_copies": 5,
        "available_copies": 5,
        "created_at": "2026-10-29T11:45:00Z",
        "updated_at": "2026-10-29T11:45:00Z"
      },
      {
        "id": 3,
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "isbn": "978-0201633610",
        "publication_year": 1994,
        "total_copies": 3,
        "available_copies": 3,
        "created_at": "2026-10-29T11:45:00Z",
        "updated_at": "2026-10-29T11:45:00Z"
      }
    ],
    "total": 2,
    "limit": 2,
    "offset": 0
  }
  ```

---

### 3.3 Get Book by ID
- **Method & Path:** `GET /api/v1/books/{book_id}`
- **Path Parameter:** `book_id` (integer >= 1)
- **Example Request:**
  ```http
  GET /api/v1/books/2 HTTP/1.1
  Host: 127.0.0.1:8000
  ```
- **Example Response (200 OK):**
  ```json
  {
    "id": 2,
    "title": "Designing Data-Intensive Applications",
    "author": "Martin Kleppmann",
    "isbn": "978-1449373320",
    "publication_year": 2017,
    "total_copies": 5,
    "available_copies": 5,
    "created_at": "2026-10-29T11:45:00Z",
    "updated_at": "2026-10-29T11:45:00Z"
  }
  ```
- **Example Error Response (404 Not Found):**
  ```json
  {
    "error": {
      "code": "BOOK_NOT_FOUND",
      "message": "Book with ID 9999 was not found.",
      "details": null
    }
  }
  ```

---

### 3.4 Create Book
- **Method & Path:** `POST /api/v1/books`
- **Request Headers:** `Content-Type: application/json`
- **Example Request Body:**
  ```json
  {
    "title": "Database System Concepts (Seventh Edition)",
    "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
    "isbn": "978-0078022159",
    "publication_year": 2019,
    "total_copies": 4
  }
  ```
- **Example Response (201 Created):**
  ```json
  {
    "id": 6,
    "title": "Database System Concepts (Seventh Edition)",
    "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
    "isbn": "978-0078022159",
    "publication_year": 2019,
    "total_copies": 4,
    "available_copies": 4,
    "created_at": "2026-10-29T12:05:00Z",
    "updated_at": "2026-10-29T12:05:00Z"
  }
  ```
- **Example Error Response (409 Conflict):**
  ```json
  {
    "error": {
      "code": "DUPLICATE_ISBN",
      "message": "A book with ISBN '978-0078022159' already exists (ID: 6).",
      "details": null
    }
  }
  ```

---

### 3.5 Replace Book (Full Update PUT)
- **Method & Path:** `PUT /api/v1/books/{book_id}`
- **Description:** Complete replacement of all book attributes. Omitted fields fail validation.
- **Example Request Body:**
  ```json
  {
    "title": "Database System Concepts (Revised Edition)",
    "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
    "isbn": "978-0078022159",
    "publication_year": 2020,
    "total_copies": 6
  }
  ```
- **Example Response (200 OK):**
  ```json
  {
    "id": 6,
    "title": "Database System Concepts (Revised Edition)",
    "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
    "isbn": "978-0078022159",
    "publication_year": 2020,
    "total_copies": 6,
    "available_copies": 6,
    "created_at": "2026-10-29T12:05:00Z",
    "updated_at": "2026-10-29T12:10:00Z"
  }
  ```

---

### 3.6 Partially Update Book (PATCH)
- **Method & Path:** `PATCH /api/v1/books/{book_id}`
- **Description:** Partial update. Only provided fields are updated; omitted fields are unchanged.
- **Example Request Body:**
  ```json
  {
    "total_copies": 8
  }
  ```
- **Example Response (200 OK):**
  ```json
  {
    "id": 6,
    "title": "Database System Concepts (Revised Edition)",
    "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
    "isbn": "978-0078022159",
    "publication_year": 2020,
    "total_copies": 8,
    "available_copies": 8,
    "created_at": "2026-10-29T12:05:00Z",
    "updated_at": "2026-10-29T12:12:00Z"
  }
  ```

---

### 3.7 Delete Book
- **Method & Path:** `DELETE /api/v1/books/{book_id}`
- **Description:** Permanently deletes book. Returns 409 Conflict if actively borrowed.
- **Example Request:**
  ```http
  DELETE /api/v1/books/6 HTTP/1.1
  Host: 127.0.0.1:8000
  ```
- **Example Success Response:** `HTTP/1.1 204 No Content` (Empty body)
- **Example Conflict Response (409 Conflict):**
  ```json
  {
    "error": {
      "code": "ACTIVE_BORROWINGS_EXIST",
      "message": "Cannot delete book with ID 6. There are 1 active borrowing records. All borrowed copies must be returned before deleting the book.",
      "details": null
    }
  }
  ```

---

### 3.8 Borrow Book
- **Method & Path:** `POST /api/v1/books/{book_id}/borrow`
- **Description:** Atomically borrows one copy of the book. Decrements `available_copies`.
- **Example Request Body:**
  ```json
  {
    "borrower_name": "Jordan Smith (Student ID: CS-305)"
  }
  ```
- **Example Response (201 Created):**
  ```json
  {
    "id": 1,
    "book_id": 2,
    "borrower_name": "Jordan Smith (Student ID: CS-305)",
    "borrowed_at": "2026-10-29T12:15:00.123456Z",
    "returned_at": null,
    "status": "BORROWED",
    "book_title": "Designing Data-Intensive Applications"
  }
  ```
- **Example Error Response (409 Conflict):**
  ```json
  {
    "error": {
      "code": "NO_COPIES_AVAILABLE",
      "message": "No copies of 'Designing Data-Intensive Applications' are currently available (0 of 5 available).",
      "details": null
    }
  }
  ```

---

### 3.9 Return Borrowed Book
- **Method & Path:** `POST /api/v1/books/{book_id}/return`
- **Description:** Marks loan as returned and increments `available_copies`.
- **Example Request Body:**
  ```json
  {
    "borrowing_id": 1
  }
  ```
- **Example Response (200 OK):**
  ```json
  {
    "id": 1,
    "book_id": 2,
    "borrower_name": "Jordan Smith (Student ID: CS-305)",
    "borrowed_at": "2026-10-29T12:15:00.123456Z",
    "returned_at": "2026-10-29T12:20:00.654321Z",
    "status": "RETURNED",
    "book_title": "Designing Data-Intensive Applications"
  }
  ```

---

### 3.10 List Borrowing Records
- **Method & Path:** `GET /api/v1/borrowings`
- **Query Parameters:**
  - `limit` (integer, default: 10, min: 1, max: 100)
  - `offset` (integer, default: 0, min: 0)
  - `status` (string, optional: `BORROWED` or `RETURNED`)
  - `book_id` (integer, optional, min: 1)
- **Example Request:**
  ```http
  GET /api/v1/borrowings?status=RETURNED&limit=5 HTTP/1.1
  Host: 127.0.0.1:8000
  ```
- **Example Response (200 OK):**
  ```json
  {
    "items": [
      {
        "id": 1,
        "book_id": 2,
        "borrower_name": "Jordan Smith (Student ID: CS-305)",
        "borrowed_at": "2026-10-29T12:15:00.123456Z",
        "returned_at": "2026-10-29T12:20:00.654321Z",
        "status": "RETURNED",
        "book_title": "Designing Data-Intensive Applications"
      }
    ],
    "total": 1,
    "limit": 5,
    "offset": 0
  }
  ```
