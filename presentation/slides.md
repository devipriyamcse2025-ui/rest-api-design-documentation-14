# Capstone 48 Presentation Slides
**Project Title:** REST API Design and Documentation Kit  
**Research Question:** *How can AI help design, test, and document a clean REST API for a small application?*  
**Audience:** Third-Year Computer Science Engineering Faculty & Students  

---

## Slide 1: Project Overview & Problem Statement
### Slide Title
**REST API Design and Documentation Kit: Clean Architecture, Automated Testing & Documentation**

### Concise Bullet Points
- **Core Question:** How can AI aid in designing, testing, and documenting a clean REST API without introducing drift or unverified bugs?
- **Target Problem:** Student APIs frequently suffer from non-standard URI verbs, contract drift between docs and code, and unhandled database edge cases.
- **Project Solution:** A complete, verified Library Management REST API built with FastAPI, SQLite, Pydantic, and automated test pipelines.
- **Academic Context:** Third-Year Computer Science & Engineering Capstone Project.
- **Team / Student Identification:** `[Student Name(s) Placeholder]` | `[Roll Number / Department Placeholder]` | `[College / University Placeholder]`

### Suggested Visual
A split diagram showing "Common Student Antipatterns" (ad-hoc URLs, manual out-of-date Word docs, unhandled 500 errors) transforming into "Clean Architecture Kit" (Resource-oriented URIs, live Swagger UI, 100% passing Pytest suite).

### Speaker Notes
> "Good morning, respected faculty and examiners. Today I am presenting our CSE Capstone Project: the REST API Design and Documentation Kit. In modern web development, REST APIs are ubiquitous, but beginner developers frequently struggle with HTTP semantics, contract drift, and domain constraints. Our project demonstrates how we can leverage AI responsibly as an engineering accelerator while utilizing automated testing and runtime reflection to guarantee complete reliability."

### Beginner-Friendly Explanation
This project is an educational, production-style reference kit that teaches students how to build a clean web service that connects mobile or web apps to a database using standard HTTP rules and automatic documentation.

---

## Slide 2: Research Foundations & REST Architectural Principles
### Slide Title
**Theoretical Foundations: REST Principles & Authoritative Standards**

### Concise Bullet Points
- **Architectural Reference:** Roy Fielding’s dissertation (2000) on REST constraints (Client-Server, Statelessness, Uniform Interface).
- **Primary Source Grounding:** RFC 9110 (HTTP Semantics), OpenAPI 3.1.0 Specification, MDN Web Docs, and OWASP API Security Top 10.
- **Uniform Interface in Action:** URLs represent nouns/resources (`/books`), while standard HTTP verbs dictate actions (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- **Eliminating Contract Drift:** Manual documentation drifts; runtime schema reflection guarantees 100% synchronization.
- **Responsible AI Mandate:** AI is utilized strictly under human supervision; all code and citations are verified against primary literature.

### Suggested Visual
A diagram illustrating the 6 REST constraints surrounding a central client-server interaction box, with icons representing MDN, OpenAPI, and RFC 9110 standards.

### Speaker Notes
> "To ground our implementation in authoritative science rather than informal tutorials, we referenced primary literature including RFC 9110 and Roy Fielding's seminal dissertation. REST requires that APIs identify resources through uniform paths and express actions using standard HTTP verbs. Furthermore, by using FastAPI's Pydantic reflection, we eliminate documentation drift because our OpenAPI specifications are generated directly from the executable code."

### Beginner-Friendly Explanation
Instead of making up our own custom web rules, we follow the official international rules that power the internet, ensuring our API works reliably with any programming language or client tool.

---

## Slide 3: System Architecture & Database Design
### Slide Title
**Layered System Architecture & Relational Persistence**

### Concise Bullet Points
- **Technology Stack:** Python 3.11, FastAPI (ASGI framework), SQLAlchemy 2.0 (ORM), SQLite (ACID persistence), Pydantic v2 (Validation).
- **Layered Clean Architecture:**
  - *Routers (`app/routers/`):* HTTP request parsing and response routing.
  - *Schemas (`app/schemas.py`):* Strict input validation, DTOs, and error envelopes.
  - *Persistence (`app/models.py`, `app/database.py`):* Relational entities and transaction management.
- **Relational Domain Entities:**
  - `Book`: Primary key, title, author, unique ISBN, publication year, total copies, available copies.
  - `Borrowing`: Primary key, foreign key (`book_id`), borrower name, timestamps, status (`BORROWED` / `RETURNED`).
- **Database Safety Invariants:** Check constraints enforce `total_copies >= 1`, `available_copies >= 0`, and `available_copies <= total_copies`.

### Suggested Visual
A Clean Architecture layered diagram displaying Presentation (FastAPI) -> Business Logic / Schemas (Pydantic) -> Persistence (SQLAlchemy ORM) -> SQLite Database (`library.db`), accompanied by the Book-to-Borrowing Entity-Relationship (ER) diagram.

### Speaker Notes
> "Our architecture separates presentation, domain validation, and database storage into clean layers. We chose SQLite for zero-configuration, reliable relational persistence. Our models enforce real-world library constraints: a book cannot have negative inventory, and active borrowings are foreign-key linked to books with strict deletion guards."

### Beginner-Friendly Explanation
Think of the system in three parts: the receptionist (FastAPI routers that receive requests), the rule checker (Pydantic schemas that check data), and the vault (SQLite database with SQLAlchemy that safely saves our records).

---

## Slide 4: Endpoint Design, HTTP Status Codes & API Versioning
### Slide Title
**RESTful Endpoint Design, Status Semantics & Versioning**

### Concise Bullet Points
- **API Versioning Strategy:** Base path versioning (`/api/v1`) ensures existing clients are not broken when future breaking changes are released.
- **Comprehensive CRUD & Workflow Endpoints:**
  - Health probe: `GET /health`
  - Books resource: `GET`, `POST /api/v1/books` | `GET`, `PUT`, `PATCH`, `DELETE /api/v1/books/{id}`
  - Borrowing workflow: `POST /api/v1/books/{id}/borrow` | `POST /api/v1/books/{id}/return` | `GET /api/v1/borrowings`
- **Precise HTTP Status Semantics:**
  - `200 OK` (Standard Read/Update) vs. `201 Created` (New Resource Instantiation).
  - `204 No Content` on successful deletion.
  - `400 Bad Request` vs. `422 Unprocessable Content` (Schema Validation Failures).
  - `404 Not Found` vs. `409 Conflict` (Duplicate ISBN, 0 available copies, active loan deletion).
- **Unified Error Envelope:** Standard schema `{ "error": { "code", "message", "details" } }` across all endpoints.

### Suggested Visual
A color-coded HTTP status code matrix showing 2xx (Green - Success), 4xx (Orange - Client/Validation Error), and 5xx (Red - Shielded Server Error), alongside the Master Endpoint Inventory Table.

### Speaker Notes
> "On this slide, you can observe our endpoint design and status code strategy. We strictly distinguish between PUT for complete replacement and PATCH for partial updates. We never return HTTP 200 with an error string. Instead, we use RFC-compliant status codes: 201 for creations, 204 for deletions, 409 for domain conflicts like duplicate ISBNs, and 422 for validation errors, all wrapped in a consistent error envelope."

### Beginner-Friendly Explanation
Every web response gives a clear numeric status code telling the client exactly what happened—whether the book was created, whether an input was invalid, or whether no copies were left to borrow.

---

## Slide 5: Demonstration, Interactive Docs & Automated Verification
### Slide Title
**Live Demonstration: Swagger UI, Pytest Suite & Automation**

### Concise Bullet Points
- **Interactive Developer Portals:**
  - Live Swagger UI at `http://127.0.0.1:8000/docs` for browser-based testing.
  - ReDoc alternate specification portal at `http://127.0.0.1:8000/redoc`.
- **Automated Pytest Suite:**
  - **22 automated tests executed** covering CRUD, boundary values, loans, and error schemas.
  - **100% Pass Rate** achieved in 1.06 seconds with zero failures.
  - Isolated temporary test database prevents test pollution of demonstration records.
- **Contract & Route Consistency Checker (`scripts/check_documentation.py`):**
  - Compares live/offline OpenAPI spec against required route inventory.
  - Returns Exit Code 0 if 100% compliant; Exit Code 1 on any route discrepancy.
- **End-to-End Live Verifier (`scripts/verify_endpoints.py`):** 11 verified live HTTP operations.

### Suggested Visual
A three-pane split graphic: Left pane showing Swagger UI interactive testing; Center pane showing the terminal output with 22 green `PASSED` Pytest tests; Right pane showing `check_documentation.py` passing with exit code 0.

### Speaker Notes
> "Here we demonstrate our verification pipeline. We don't merely claim our API works; we prove it through automation. When we start the server, faculty can test every endpoint through Swagger UI. Behind the scenes, our Pytest suite runs 22 comprehensive tests in one second against an isolated test database. Additionally, our custom documentation checking script inspects the OpenAPI schema and confirms zero contract drift."

### Beginner-Friendly Explanation
We built automated robots (scripts and test cases) that thoroughly test every single button and feature of our API, ensuring everything works perfectly before we ever present it.

---

## 6. Slide 6: Results, Limitations, Ethics & Future Enhancements
### Slide Title
**Empirical Results, Responsible AI, Ethics & Roadmap**

### Concise Bullet Points
- **Empirical Results:**
  - 22 / 22 Pytest tests passing (100%).
  - 11 / 11 core routes documented and verified without drift.
  - Sub-second automated regression testing.
- **Responsible AI & Ethics:**
  - AI used as a supervised accelerator; zero unverified or hallucinated citations.
  - Privacy by design: Synthetic student personas only; zero real student PII collected.
  - Secure by design: No API keys committed; internal stack traces shielded from clients.
- **Identified Limitations:**
  - SQLite database-level locking ceilings under high write concurrency.
  - Authentication omitted from v1 to keep student demonstration focused on REST fundamentals.
- **Future v2 Roadmap:**
  - OAuth2 password grant with JWT bearer tokens & Role-Based Access Control (RBAC).
  - Multi-user rate limiting via Redis token bucket.
  - Migration to PostgreSQL for cloud-native distributed deployments.

### Suggested Visual
A road-mapping flowchart depicting Phase 1 (Core REST, Verification, Documentation — Completed) transitioning to Phase 2 (JWT Auth, RBAC, PostgreSQL, Docker — Future Work), with an "Ethics & Verification Stamp" guarantee.

### Speaker Notes
> "In conclusion, Capstone 48 successfully demonstrates how AI can assist in engineering clean, verified REST APIs when guided by strong architectural discipline. We achieved 100% passing tests and complete contract consistency while upholding privacy and security principles. For future work, we have architected an OAuth2 JWT authentication layer for Version 2. Thank you, and I am now ready for questions."

### Beginner-Friendly Explanation
We completed a fully functioning, verified system that adheres to real-world engineering ethics. We understand its current boundaries and have a clear engineering plan for how to expand it with logins and passwords in the future.
