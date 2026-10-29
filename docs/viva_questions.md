# Capstone Viva Voce Preparation Guide
**Project:** REST API Design and Documentation Kit (Capstone 48)  
**Target Audience:** Third-Year Computer Science & Engineering Students Facing Faculty Evaluation  

This guide provides direct, technically precise answers to the 15 most probable viva voce questions faculty examiners will ask about your REST API capstone project.

---

### Q1: What is REST and what are its core architectural constraints?
**Answer:**  
REST stands for **Representational State Transfer**, an architectural style introduced by Dr. Roy Fielding in 2000 for distributed hypermedia systems. Its core constraints are:
1. **Client-Server Architecture:** Separation of user interface concerns from data storage.
2. **Statelessness:** Each HTTP request must contain all necessary information for the server to fulfill it; no client session state is preserved on the server between requests.
3. **Cacheability:** Responses must explicitly declare whether they can be cached.
4. **Uniform Interface:** Resources are identified via standard URIs, manipulated through standard HTTP methods, and represented in standard media types (like JSON).
5. **Layered System:** Clients cannot distinguish between communicating directly with the end server or an intermediate proxy.

---

### Q2: What is an API and how does a Web API differ from a library API?
**Answer:**  
An **Application Programming Interface (API)** is a formal contract specifying how software components communicate.
- A **Library API** (such as Python's `math` module) operates within the same memory address space via local in-process function calls.
- A **Web API** operates across network boundaries over protocols like HTTP, using serialized data formats (such as JSON or XML) to enable heterogeneous systems written in different programming languages to exchange data seamlessly.

---

### Q3: Why did you choose FastAPI over Flask or Django?
**Answer:**  
FastAPI was chosen because:
1. **Native OpenAPI Generation:** It automatically generates interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) directly from Python code and type hints, eliminating documentation drift.
2. **Pydantic Validation:** Request and response schemas are strictly validated at runtime using standard Python type annotations.
3. **High Performance:** Built on Starlette and ASGI, FastAPI supports asynchronous concurrency out of the box.
4. **Modern Clean Architecture:** It provides built-in dependency injection (`Depends`), making database session management and test overrides clean and modular.

---

### Q4: Why did you use SQLite for database persistence?
**Answer:**  
SQLite is a zero-configuration, serverless, self-contained relational database engine that stores all data in a single local disk file (`library.db`).
- For a student capstone project, it eliminates the overhead and prerequisites of installing, configuring, and administering heavy external database servers (like MySQL or PostgreSQL).
- It provides full ACID transaction guarantees and is fully supported by SQLAlchemy ORM, while remaining completely free and cross-platform.

---

### Q5: What is the OpenAPI Specification (OAS)?
**Answer:**  
The OpenAPI Specification (formerly Swagger) is a vendor-neutral, machine-readable standard (in JSON or YAML) for describing modern REST APIs. It defines:
- All available paths and HTTP operations.
- Input parameters (path, query, headers, body) and their data types.
- Output response models, HTTP status codes, and error envelopes.
- Security and authentication schemes.
It allows automated tools to generate interactive documentation, client SDKs, and automated test runners without inspecting backend source code.

---

### Q6: What is Swagger UI and how does it relate to OpenAPI?
**Answer:**  
OpenAPI is the **machine-readable specification document** (`/openapi.json`).  
Swagger UI is the **interactive web application** (rendered at `/docs`) that reads that OpenAPI JSON document and generates a visual, human-friendly portal where developers and faculty can view endpoint descriptions, inspect schemas, and execute live API requests directly from their browser.

---

### Q7: Why is API versioning important, and why did you use URI versioning?
**Answer:**  
API versioning ensures **backward compatibility**. As business logic evolves, new features must not break existing client applications running older software.
We chose **URI Versioning (`/api/v1`)** because:
- It is explicit, discoverable, and easily testable in browsers and documentation.
- It allows routing breaking changes (e.g. `/api/v2`) to different route controllers while keeping `/api/v1` intact.
- Breaking changes include removing fields, renaming attributes, or altering validation types; non-breaking changes (like adding optional query filters) can safely remain in the current version.

---

### Q8: What is the precise difference between HTTP PUT and HTTP PATCH?
**Answer:**  
- **PUT (Complete Replacement):** Replaces the target resource representation in its entirety. The client must supply all required attributes of the resource. If fields are omitted, they are reset or rejected. It is idempotent: executing `PUT` once has the exact same side-effect as executing it multiple times with the same body.
- **PATCH (Partial Modification):** Applies partial mutations to the resource. The client only sends the specific attributes it wishes to change (e.g. updating only `total_copies`). Omitted attributes remain unchanged.

---

### Q9: When should you return HTTP 200 OK versus HTTP 201 Created?
**Answer:**  
- **200 OK:** Returned when a request succeeds and returns data or acknowledges modification of an existing resource (used in `GET`, `PUT`, `PATCH`, and return operations).
- **201 Created:** Strictly returned when a request results in the **instantiation of a new persistent resource** with a newly assigned primary key identifier (used in `POST /api/v1/books` and `POST /api/v1/books/{id}/borrow`).

---

### Q10: What is the difference between HTTP 400 Bad Request and HTTP 422 Unprocessable Content?
**Answer:**  
- **422 Unprocessable Content (RFC 9110):** The server understands the content type and syntax of the request, but the payload contains semantic or schema validation errors (e.g. passing a string to an integer field, or providing a negative publication year). Pydantic automatically handles this.
- **400 Bad Request:** The request passes syntactic schema validation, but violates higher-level domain business logic that schemas cannot evaluate (e.g. attempting to reduce a book's total copies to a number lower than the count of currently active borrowed copies).

---

### Q11: What is the difference between HTTP 404 Not Found and HTTP 409 Conflict?
**Answer:**  
- **404 Not Found:** The resource URI does not match any existing record in the database (e.g. `GET /api/v1/books/9999`).
- **409 Conflict:** The target resource exists, but executing the requested operation would violate an existing database state or business policy. Examples in our kit:
  1. Creating a book whose ISBN already exists (`DUPLICATE_ISBN`).
  2. Borrowing a book when `available_copies == 0` (`NO_COPIES_AVAILABLE`).
  3. Deleting a book that currently has active, unreturned borrowings (`ACTIVE_BORROWINGS_EXIST`).

---

### Q12: Why is automated testing necessary for REST APIs?
**Answer:**  
Manual testing (e.g. clicking through Swagger UI) is slow, subjective, and prone to human oversight. Automated testing:
- Validates that code meets specifications deterministically on every commit.
- Prevents regressions when refactoring business logic.
- Enables exhaustive testing of edge cases (negative numbers, boundary checks, duplicate keys) in milliseconds.
Our project includes 22 automated test cases running in under 2 seconds.

---

### Q13: Why did you use an isolated test database instead of testing on your live database?
**Answer:**  
If automated tests execute against the demonstration or production database, they create dirty test data, consume inventory, and risk corrupting persistent state.
In `tests/conftest.py`, we override the database dependency to use an **isolated, temporary database session** that recreates tables fresh before each test. This guarantees:
1. **Zero side-effects:** Demonstration books remain untouched.
2. **Reproducibility:** Tests run with identical baseline state every time.
3. **Speed:** In-memory or temporary SQLite databases execute rapidly.

---

### Q14: How does your endpoint documentation consistency checker work?
**Answer:**  
`scripts/check_documentation.py` is an automation script that:
1. Loads the OpenAPI specification (from the live running server, saved `openapi.json`, or the FastAPI application object).
2. Extracts all documented routes and HTTP methods.
3. Compares them against an authoritative predefined dictionary of required endpoints.
4. Detects missing endpoints or mismatched HTTP verbs.
5. Returns exit code 1 if discrepancies exist, and exit code 0 only if 100% compliant.
This ensures continuous contract synchronization in CI/CD pipelines.

---

### Q15: What are the risks and limitations of AI-generated code in software engineering?
**Answer:**  
1. **Hallucination of APIs & Libraries:** AI may invent non-existent functions or import obsolete packages.
2. **Subtle Concurrency & Security Bugs:** AI code may look syntactically correct while introducing race conditions, unhandled database rollbacks, or exposed stack traces.
3. **Lack of Domain Accountability:** AI has no legal or professional responsibility; developers must review every line.
In this project, AI was utilized strictly under human supervision for scaffolding, while deterministic compilers, type linters, and a 22-case pytest suite verified every invariant.
