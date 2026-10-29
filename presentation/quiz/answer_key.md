# Capstone 48: Quiz Answer Key & Explanations
**Project:** REST API Design and Documentation Kit  
**Target Level:** Third-Year Computer Science & Engineering Undergraduates  

---

### Answer 1
- **Correct Option:** **B) Every request from a client to the server must contain all of the information needed to understand and process the request (Statelessness).**
- **Explanation:** Statelessness is a non-negotiable REST constraint. The server stores no conversational session state between requests. Option A violates statelessness. Option C violates uniform interface (REST uses nouns for URIs, not verbs). Option D is incorrect because REST is format-agnostic (JSON is standard in modern web APIs).

---

### Answer 2
- **Correct Answer:**
  - **Safe Method:** An HTTP method is safe if it does not alter server state or produce side-effects (read-only).
  - **Idempotent Method:** An HTTP method is idempotent if executing it multiple times with the same parameters produces the exact same server state as executing it once (`f(f(x)) = f(x)`).
  - **Categorization:**
    - `GET`: **Safe and Idempotent**.
    - `PUT`: **Not Safe, but Idempotent** (repeated complete replacements result in the identical resource state).
    - `DELETE`: **Not Safe, but Idempotent** (repeated deletions produce the same result: resource is absent).
    - `POST`: **Neither Safe nor Idempotent** (repeated POST requests create duplicate resources or execute multiple state transitions).

---

### Answer 3
- **Correct Option:** **D) `409 Conflict`**
- **Explanation:** RFC 9110 specifies that `409 Conflict` must be returned when the request cannot be completed due to a conflict with the current state of the target resource. A duplicate unique key (such as an existing ISBN) is a classic database state conflict. Option A is an antipattern. Option B is for general client errors. Option C is when a target resource is missing.

---

### Answer 4
- **Correct Answer:**
  - **Path Parameter:** Used to identify a specific, unique resource instance in the hierarchical URI structure.
    - *Example:* `/api/v1/books/5` where `5` targets the specific book with primary key ID 5.
  - **Query Parameter:** Used to filter, sort, paginate, or modify the representation of a resource collection without altering its identity.
    - *Example:* `/api/v1/books?limit=10&search=martin` where `limit` and `search` filter the books collection.

---

### Answer 5
- **Correct Option:** **A) To ensure that future breaking changes can be deployed in a new path (e.g. `/api/v2`) without breaking older client applications.**
- **Explanation:** API versioning protects backward compatibility. Legacy mobile apps or third-party integrations consuming `/api/v1` can continue operating smoothly while new clients adopt breaking alterations in `/api/v2`.

---

### Answer 6
- **Correct Answer:**
  - **OpenAPI Specification (OAS):** The standardized, machine-readable JSON/YAML schema format describing API paths, parameters, schemas, and responses.
  - **Swagger UI:** The browser-based visual user interface that renders the OpenAPI JSON document, allowing interactive exploratory testing.
  - **FastAPI Mechanism:** FastAPI automatically generates the OpenAPI schema at runtime by inspecting Python type hints and Pydantic schema models via Python's Abstract Syntax Tree (AST), ensuring code and documentation never drift.

---

### Answer 7
- **Correct Option:** **C) `422 Unprocessable Content` (or Unprocessable Entity)**
- **Explanation:** Under RFC 9110 and FastAPI / Pydantic standards, when a request payload is syntactically well-formed (valid JSON) but contains values that fail schema validation rules or type coercion, the server emits HTTP 422 with a structured error details list.

---

### Answer 8
- **Correct Answer:**
  - **Security Rationale:** Exposing raw stack traces, SQL syntax snippets, table structures, or operating system paths introduces an Information Leakage vulnerability (OWASP API8: Security Misconfiguration). Malicious attackers use this internal diagnostic data to craft targeted exploits and SQL injection payloads.
  - **Correct Practice:** The internal details should be logged to secure server stdout/log files. The HTTP response should return a sanitized, standardized JSON error envelope:
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

### Answer 9
- **Correct Option:** **B) To prevent test runs from polluting, mutating, or destroying persistent demonstration data and to guarantee reproducible baseline state.**
- **Explanation:** Automated testing requires clean, predictable fixtures. If tests run against the primary demonstration database, creating, deleting, and borrowing books would alter real demonstration records and cause tests to fail intermittently based on previous runs.

---

### Answer 10
- **Correct Answer:**
  - **Two Risks:**
    1. *Hallucinated APIs & Libraries:* AI frequently invents non-existent methods, deprecated library parameters, or incorrect status codes that look plausible but fail at runtime.
    2. *Hidden Concurrency & Business Logic Bugs:* AI code may appear syntactically correct while introducing race conditions, negative inventory, or unhandled database rollbacks.
  - **Our Project Mitigation:**
    All AI-assisted scaffolding was grounded in official specifications (MDN, OpenAPI, FastAPI) and verified through a 22-case automated Pytest suite and automated route consistency linters (`check_documentation.py`) executed against isolated databases.
