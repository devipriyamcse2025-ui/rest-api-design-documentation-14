# Capstone 48: REST API Engineering Knowledge Quiz
**Project:** REST API Design and Documentation Kit  
**Target Level:** Third-Year Computer Science & Engineering Undergraduates  
**Instructions:** Answer all 10 questions. The quiz contains a mixture of Multiple-Choice Questions (MCQ) and Short-Answer Questions. Total Time: 20 Minutes.

---

### Question 1 (REST Architectural Principles) — Multiple Choice
According to Roy Fielding's REST architectural style, which of the following is an essential constraint of REST?
- **A)** The server must maintain in-memory session state for each authenticated client between requests.
- **B)** Every request from a client to the server must contain all of the information needed to understand and process the request (Statelessness).
- **C)** All endpoint URIs must contain action verbs such as `/create`, `/update`, or `/delete`.
- **D)** APIs must exclusively use XML as their data exchange payload format.

---

### Question 2 (HTTP Methods & Idempotency) — Short Answer
Explain the technical difference between an **idempotent** HTTP method and a **safe** HTTP method. Categorize `GET`, `POST`, `PUT`, and `DELETE` into safe and/or idempotent.

---

### Question 3 (HTTP Status Codes) — Multiple Choice
A client attempts to create a new book in the library using `POST /api/v1/books`. The request payload is syntactically valid JSON, but the supplied `isbn` already exists in the database. Which HTTP status code should the server return according to RFC 9110?
- **A)** `200 OK` with an error message in the response body.
- **B)** `400 Bad Request`
- **C)** `404 Not Found`
- **D)** `409 Conflict`

---

### Question 4 (Path vs. Query Parameters) — Short Answer
In RESTful URL design, what is the functional difference between a **Path Parameter** and a **Query Parameter**? Give one example of each from the Library Management API.

---

### Question 5 (API Versioning) — Multiple Choice
Why is URI path versioning (such as `/api/v1`) commonly implemented in REST APIs?
- **A)** To ensure that future breaking changes can be deployed in a new path (e.g. `/api/v2`) without breaking older client applications.
- **B)** Because HTTP protocols do not support APIs without version numbers in the path.
- **C)** To encrypt all outgoing network traffic automatically.
- **D)** To bypass database indexing and speed up queries.

---

### Question 6 (OpenAPI Specification) — Short Answer
What is the relationship between the **OpenAPI Specification (OAS)** and **Swagger UI**? How does FastAPI generate them?

---

### Question 7 (Request Validation & Pydantic) — Multiple Choice
When a client sends a request to FastAPI where a required integer field `publication_year` is sent as a string `"nineteen-ninety"`, what HTTP status code does FastAPI automatically return by default?
- **A)** `400 Bad Request`
- **B)** `404 Not Found`
- **C)** `422 Unprocessable Content` (or Unprocessable Entity)
- **D)** `500 Internal Server Error`

---

### Question 8 (Error Handling Architecture) — Short Answer
Why should a REST API's `500 Internal Server Error` handler **never** return raw Python stack traces, SQL queries, or database error strings to the client? What should it return instead?

---

### Question 9 (Automated API Testing) — Multiple Choice
Why is it critical for automated integration test suites (such as Pytest with FastAPI TestClient) to use an isolated temporary or in-memory database rather than the primary demonstration database?
- **A)** Because SQLite cannot store more than 10 records at a time.
- **B)** To prevent test runs from polluting, mutating, or destroying persistent demonstration data and to guarantee reproducible baseline state.
- **C)** Because Pytest cannot connect to persistent disk files.
- **D)** To bypass input validation schemas during test execution.

---

### Question 10 (Responsible AI in Engineering) — Short Answer
State two major technical or ethical risks of blindly trusting AI-generated code in backend software development, and explain how our capstone project methodology mitigated them.
