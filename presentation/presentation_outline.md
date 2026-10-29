# Capstone 48: Presentation Outline & Speaker Script
**Project:** REST API Design and Documentation Kit  
**Format:** 6-Slide Presentation + Live Demo + Viva Q&A (Total Duration: 10–12 Minutes)  
**Target Audience:** Computer Science & Engineering Faculty Examination Committee  

---

## 1. Presentation Structure & Timing Overview

| Segment | Duration | Content / Activity | Slide Reference |
|---------|----------|--------------------|-----------------|
| **Introduction** | 1.5 min | Problem statement, objectives, and research question | Slide 1 |
| **Theory & Standards** | 2.0 min | REST principles, RFC 9110, OpenAPI, primary sources | Slide 2 |
| **Architecture & Database** | 2.0 min | Layered architecture, SQLite persistence, models | Slide 3 |
| **API Design & Status Codes** | 2.0 min | Resource routing, versioning, unified error format | Slide 4 |
| **Live Demo & Test Pipeline** | 2.5 min | Swagger UI demo, 22-test Pytest run, doc checker | Slide 5 |
| **Conclusion & Ethics** | 1.5 min | Results, responsible AI, limitations, v2 roadmap | Slide 6 |
| **Faculty Q&A (Viva)** | 3.0 min | Defense of implementation, status codes, concurrency | Viva Guide |

---

## 2. Slide-by-Slide Script & Delivery Instructions

### Slide 1: Project Overview & Problem Statement (0:00 – 1:30)
- **Objective:** Introduce yourself, establish the academic importance of the project, and state the core research question clearly.
- **Key Talking Points:**
  - Introduce your name and roll number.
  - State that REST APIs are the standard communication mechanism in modern distributed software.
  - Highlight the common student pitfalls: using verb-based URLs, writing outdated documentation, and ignoring HTTP status codes.
  - Introduce the core research question: *How can AI help design, test, and document a clean REST API for a small application responsibly?*
- **Transition:** *"To answer this question rigorously, we began by examining the authoritative engineering standards that govern web protocols..."*

### Slide 2: Research Foundations & REST Architectural Principles (1:30 – 3:30)
- **Objective:** Demonstrate that the project is anchored in primary scientific literature, not casual blog posts.
- **Key Talking Points:**
  - Reference Roy Fielding’s 2000 doctoral dissertation defining REST (Client-Server, Statelessness, Uniform Interface).
  - Emphasize primary sources: RFC 9110 (HTTP Semantics), OpenAPI 3.1.0 Specification, and OWASP API Security Top 10.
  - Explain why manual documentation fails (documentation drift) and how runtime schema reflection from Pydantic models guarantees 100% synchronization.
  - Emphasize our responsible AI principle: AI serves as a supervised accelerator, while deterministic tests verify every claim.
- **Transition:** *"Now let us examine how these theoretical constraints translate into our layered system architecture..."*

### Slide 3: System Architecture & Database Design (3:30 – 5:30)
- **Objective:** Explain the system layers and relational persistence model.
- **Key Talking Points:**
  - Walk through the stack: Python 3.11, FastAPI, SQLAlchemy 2.0, SQLite, and Pydantic v2.
  - Explain the Clean Architecture layers: Routers (presentation) -> Schemas (validation) -> Models/Database (persistence).
  - Walk through the two core relational entities: `Book` and `Borrowing`.
  - Highlight database safety constraints: SQLite `CHECK` constraints ensuring total copies >= 1, available copies >= 0, and available copies never exceed total copies.
- **Transition:** *"Next, let us look at the external contract: how our endpoints and status codes are designed..."*

### Slide 4: Endpoint Design, HTTP Status Codes & API Versioning (5:30 – 7:30)
- **Objective:** Showcase adherence to RFC status codes, versioning, and unified error handling.
- **Key Talking Points:**
  - Explain why URI path versioning (`/api/v1`) was chosen (clarity, ease of demonstration, backward compatibility).
  - Highlight endpoint operations: Health probe, Book CRUD, and Borrow/Return workflow.
  - Clarify critical HTTP status distinctions:
    - `200 OK` vs `201 Created` (new resource instantiation).
    - `204 No Content` on successful deletion.
    - `400 Bad Request` vs `422 Unprocessable Content` (schema validation vs business logic).
    - `404 Not Found` vs `409 Conflict` (duplicate ISBNs, zero available copies, deleting active loans).
  - Show the standardized error envelope: `{ "error": { "code", "message", "details" } }`.
- **Transition:** *"Now, let us move from architecture to empirical proof with a live demonstration of our system..."*

### Slide 5: Demonstration, Interactive Docs & Automated Verification (7:30 – 10:00)
- **Objective:** Demonstrate live execution and show real automated test results.
- **Key Talking Points:**
  - Open browser or terminal to show Swagger UI at `http://127.0.0.1:8000/docs`.
  - Show the 22 automated Pytest test cases passing with 100% success rate in approximately one second.
  - Highlight test database isolation: tests use an isolated temporary database, so demonstration data remains intact.
  - Run or highlight `scripts/check_documentation.py`: explain how it automates OpenAPI route verification to prevent contract drift with exit code 0.
  - Run or highlight `scripts/verify_endpoints.py`: showing 11 automated live HTTP operations.
- **Transition:** *"Finally, let us review our empirical findings, ethical safeguards, and future enhancements..."*

### Slide 6: Results, Limitations, Ethics & Future Enhancements (10:00 – 11:30)
- **Objective:** Summarize verified results, acknowledge engineering limitations honestly, and state future work.
- **Key Talking Points:**
  - Reiterate verified numbers: 22/22 tests passed, 11/11 endpoints documented, zero route drift.
  - Review ethical practices: Zero real student PII (synthetic personas only), no API keys in Git, no leaked stack traces.
  - Transparently state limitations: SQLite write concurrency ceilings, and intentional omission of authentication in v1 to preserve pedagogical focus.
  - Present the v2 roadmap: OAuth2/JWT authentication, Role-Based Access Control (RBAC), and containerization with Docker.
- **Closing Statement:** *"Thank you, respected faculty. Our complete source code, verification reports, and documentation are available for your inspection. I welcome your questions."*

---

## 3. Recommended Faculty Demonstration Flow
When presenting live in front of faculty:
1. **Step 1 (30 seconds):** Open terminal and run `.\run.bat` (or `pytest -v`). Show the 22 green passed tests.
2. **Step 2 (30 seconds):** Run `python scripts/check_documentation.py` to demonstrate the automated consistency checker passing with exit code 0.
3. **Step 3 (1 minute):** Open browser to `http://127.0.0.1:8000/docs` (Swagger UI). Execute a `GET /api/v1/books` request to show live data.
4. **Step 4 (1 minute):** Demonstrate an intentional failure in Swagger UI (e.g. attempting to create a book with year `2099` or duplicate ISBN) to showcase the unified 422 or 409 error envelope.
