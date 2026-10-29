# HTTP Status Codes & Error Handling Architecture
**Project:** REST API Design and Documentation Kit (Capstone 48)  
**Standard Reference:** RFC 9110 (HTTP Semantics)  

---

## 1. Status Code Philosophy in REST APIs
In a RESTful architecture, HTTP status codes serve as the primary communication signal indicating the outcome of a client's request. A common antipattern in student projects is returning `200 OK` for every request with an internal status code embedded in the payload (e.g. `{ "status": 404, "error": "Not Found" }`). This breaks HTTP intermediary caching, proxies, reverse-proxies, monitoring alerts, and standard client libraries.

In this project, every response uses an RFC-compliant HTTP status code in the response line, coupled with a predictable, machine-readable JSON error envelope whenever a non-2xx outcome occurs.

---

## 2. Status Code Reference Table

| Code | Standard HTTP Reason | When It Is Used in This Project | Example Trigger |
|------|----------------------|---------------------------------|-----------------|
| `200` | **OK** | Successful read, full/partial update, or return operation | `GET /api/v1/books`, `PUT`, `PATCH`, return book |
| `201` | **Created** | Successful creation of a new persistent resource | `POST /api/v1/books`, `POST /api/v1/books/{id}/borrow` |
| `204` | **No Content** | Successful deletion with zero response body payload | `DELETE /api/v1/books/{id}` (when permitted) |
| `400` | **Bad Request** | Syntactically valid request violates business invariants | Reducing total copies below active borrowed count |
| `404` | **Not Found** | Target resource or subordinate identifier does not exist | `GET /api/v1/books/99999` |
| `409` | **Conflict** | Request conflicts with current database state | Duplicate ISBN, 0 available copies, active loan delete |
| `422` | **Unprocessable Content** | Request payload or parameter failed schema validation | Negative publication year, string passed to integer ID |
| `500` | **Internal Server Error** | Unexpected unhandled failure inside application code | Uncaught database crash, disk exhaustion |

---

## 3. Deep-Dive: When to Use Each Status Code

### 200 OK vs. 201 Created
- **200 OK:** Indicates standard success where the server returns data or acknowledges modification of an existing resource. Used for all `GET`, `PUT`, and `PATCH` endpoints.
- **201 Created:** Strictly reserved for requests that instantiate a *new* identifiable resource with its own persistent identifier. Used when creating a new Book record or generating a new Borrowing transaction record.

### 200 OK vs. 204 No Content
- **200 OK:** The server fulfilled the request and returns a representation in the message body.
- **204 No Content:** The server successfully fulfilled the request and there is no additional content to send in the response payload. RFC 9110 states that responses to `DELETE` may return 204 when no representation is returned. Our `DELETE /api/v1/books/{id}` returns 204 with an empty body.

### 400 Bad Request vs. 422 Unprocessable Content
- **422 Unprocessable Content (RFC 9110):** The request was syntactically correct and parsed successfully (e.g. valid JSON), but contained semantic or type validation errors (e.g. `publication_year: "two-thousand"`, or `total_copies: -5`). Pydantic v2 automatically routes validation failures to 422.
- **400 Bad Request:** Used when the input passes structural schema validation, but violates higher-level domain rules that cannot be evaluated by the schema alone (e.g., trying to set `total_copies = 2` when 3 copies are currently loaned out).

### 404 Not Found vs. 409 Conflict
- **404 Not Found:** The resource target of the request does not exist in the system.
- **409 Conflict:** The target resource exists, but processing the request would result in an irreconcilable conflict with current server state. Examples:
  1. Creating a book with an ISBN that already belongs to another book (`DUPLICATE_ISBN`).
  2. Borrowing a book whose `available_copies == 0` (`NO_COPIES_AVAILABLE`).
  3. Deleting a book that currently has active unreturned loans (`ACTIVE_BORROWINGS_EXIST`).

### 500 Internal Server Error & Information Hiding
- **500 Internal Server Error:** Indicates an unforeseen runtime catastrophe.
- **Crucial Security Guideline:** In production and academic capstones, a 500 handler must **never** leak raw Python stack traces, SQL syntax snippets, database table names, or file paths to the client. Attackers use exposed stack traces to map internal vulnerabilities (OWASP API Security Top 10: API8 - Security Misconfiguration).
- In our application, unhandled exceptions log the traceback to the internal server console, while returning a sanitized JSON response:
  ```json
  {
    "error": {
      "code": "INTERNAL_SERVER_ERROR",
      "message": "An unexpected internal server error occurred. Please contact the administrator.",
      "details": null
    }
  }
  ```

---

## 4. Standard Error Response Envelope
Every error response generated by the application conforms to a unified schema:
```json
{
  "error": {
    "code": "MACHINE_READABLE_UPPERCASE_CODE",
    "message": "Human-readable explanation of the issue.",
    "details": null
  }
}
```

### Example: 422 Validation Error
When a client sends an invalid request:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request payload or parameters failed schema validation.",
    "details": [
      {
        "field": "body -> publication_year",
        "message": "Value error, publication_year must be between 1000 and 2026.",
        "type": "value_error"
      }
    ]
  }
}
```

### Example: 409 Active Borrowings Exist
When attempting to delete a book with unreturned copies:
```json
{
  "error": {
    "code": "ACTIVE_BORROWINGS_EXIST",
    "message": "Cannot delete book with ID 2. There are 2 active borrowing records. All borrowed copies must be returned before deleting the book.",
    "details": null
  }
}
```
