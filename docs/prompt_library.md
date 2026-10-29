# Capstone Prompt Library: AI Engineering Prompts & Verification
**Project:** REST API Design and Documentation Kit (Capstone 48)  
**Standard Reference:** Responsible AI Software Engineering Framework  

---

## 1. Introduction
This library contains the ten core prompts used or recommended for building, testing, verifying, and documenting the REST API Design and Documentation Kit. 

In accordance with responsible engineering principles, prompts are categorized as:
- **[EXECUTED IN PROJECT]** — Prompts utilized directly in the design, scaffolding, and verification of this capstone repository.
- **[REUSABLE TEMPLATE]** — Formalized prompt templates provided for future student extensions, code reviews, and production auditing.

---

## 2. Prompts Catalog

### Prompt 1: Requirements Analysis & Domain Modeling
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Break down college capstone requirements into entities, domain invariants, and relational schemas.
- **Prompt:**
  ```text
  Act as a senior software architect. Analyze the requirements for a Library Management REST API designed for third-year CSE students.
  Identify:
  1. The core entities and their relational foreign keys (Book, Borrowing).
  2. The necessary database constraints (positive copies, ISBN uniqueness, non-negative available inventory).
  3. The business invariants (preventing loans when inventory is 0, blocking deletion of actively borrowed books).
  Produce a concise entity-relationship summary and state-transition model.
  ```
- **Expected Output:** Structured entity attribute list, foreign key constraints, and lifecycle state machines.
- **Verification Method:** Verified against domain rules in `app/models.py` and validated by SQLite check constraints.

---

### Prompt 2: REST API Architecture & Resource-Oriented URI Design
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Design clean, resource-oriented URIs adhering strictly to RFC 9110 HTTP semantics without RPC anti-patterns.
- **Prompt:**
  ```text
  Design a complete RESTful URI route map for a Library Management system using the versioned prefix /api/v1.
  Map each operation to the correct HTTP method (GET, POST, PUT, PATCH, DELETE) and appropriate status codes (200, 201, 204, 400, 404, 409, 422).
  Ensure:
  - URLs use plural nouns, not verbs.
  - Sub-resources represent relationships (e.g. /api/v1/books/{id}/borrow).
  - Explicit distinction between PUT (full replacement) and PATCH (partial update).
  Provide a markdown table summarizing method, path, action, and expected status codes.
  ```
- **Expected Output:** Formal endpoint table with HTTP verbs and status codes.
- **Verification Method:** Checked via `scripts/check_documentation.py` and cross-referenced with MDN HTTP documentation.

---

### Prompt 3: Pydantic v2 Schema & FastAPI Route Scaffolding
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Generate type-annotated Pydantic v2 models and FastAPI route signatures with validation rules.
- **Prompt:**
  ```text
  Write Python 3.11 Pydantic v2 schemas and FastAPI APIRouters for the Books and Borrowings resources.
  Requirements:
  - Enforce field validations: ISBN regex check, publication_year between 1000 and current year, total_copies >= 1.
  - Implement Paginated envelope schemas (items, total, limit, offset).
  - Implement standardized ErrorEnvelope schema: {"error": {"code": str, "message": str, "details": any}}.
  - Use modern FastAPI dependencies for database sessions.
  ```
- **Expected Output:** Python code containing Pydantic models with `@field_validator` and APIRouter definitions.
- **Verification Method:** Python AST compilation and automated pytest validation suite.

---

### Prompt 4: Code Review & Anti-Pattern Detection
- **Status:** `[REUSABLE TEMPLATE]`
- **Purpose:** Audit generated FastAPI and SQLAlchemy code for performance bottlenecks, transaction leaks, and security oversights.
- **Prompt:**
  ```text
  Conduct a rigorous code review of the attached FastAPI and SQLAlchemy router code.
  Look specifically for:
  1. Transaction safety: Are db.commit() and db.rollback() calls structured to prevent orphan sessions on error?
  2. Information disclosure: Are internal database exceptions or stack traces ever returned to the client?
  3. Status code correctness: Are any 200 OK responses returned with embedded error messages?
  4. N+1 query problems in SQLAlchemy queries.
  Provide concrete recommendations with corrected Python code snippets.
  ```
- **Expected Output:** Annotated code review identifying specific security, transactional, or stylistic bugs.
- **Verification Method:** Static code analysis via linters (`flake8`, `mypy`) and manual peer review.

---

### Prompt 5: Adversarial Pytest Test-Case Generation
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Generate exhaustive automated test cases covering happy paths, negative boundaries, and domain conflicts.
- **Prompt:**
  ```text
  Write a comprehensive pytest test suite using FastAPI TestClient and an isolated temporary SQLite database.
  Cover:
  1. Successful CRUD on Books.
  2. 409 Conflict on duplicate ISBN.
  3. 422 Unprocessable Content on future publication years and negative copies.
  4. Concurrency boundary: Attempting to borrow when available_copies == 0.
  5. Policy boundary: Attempting to delete a book with active unreturned borrowings.
  6. Return operation restoring available copies.
  7. Verification of standardized error envelope format on 404 and 422.
  ```
- **Expected Output:** Pytest Python test files (`test_books.py`, `test_borrowings.py`, `test_errors.py`).
- **Verification Method:** Direct execution of `pytest -v`, ensuring 100% of the 22 tests pass without regressions.

---

### Prompt 6: OpenAPI Schema & Documentation Synthesis
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Configure OpenAPI metadata, docstrings, route summaries, and export scripts.
- **Prompt:**
  ```text
  Enhance the FastAPI application definition with detailed OpenAPI metadata:
  - Title, semantic version, and educational description.
  - Group routes using tags_metadata ("Health", "Books", "Borrowing").
  - Add realistic JSON request and response examples to Pydantic schemas.
  - Create a Python script scripts/generate_openapi.py to dump the live OpenAPI schema to openapi/openapi.json.
  ```
- **Expected Output:** Enriched FastAPI app configuration and export script.
- **Verification Method:** Run `scripts/generate_openapi.py` and inspect `openapi/openapi.json` with Swagger UI.

---

### Prompt 7: Technical Research & Primary Source Grounding
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Structure the academic research report around primary specifications rather than secondary blog posts.
- **Prompt:**
  ```text
  Draft an academic research report for CSE Capstone 48 titled 'REST API Design and Documentation Kit'.
  Ground all architectural claims in primary sources:
  1. RFC 9110 (HTTP Semantics)
  2. Roy Fielding's doctoral dissertation on REST (2000)
  3. OpenAPI 3.1.0 Specification
  4. Official FastAPI & Pydantic documentation
  5. OWASP API Security Top 10
  Structure the paper with Abstract, Problem Statement, Objectives, Methodology, Empirical Results, Limitations, and References.
  Do not hallucinate citations or performance numbers.
  ```
- **Expected Output:** Formal academic markdown document with complete citations and access dates.
- **Verification Method:** Manual URL and citation validation against MDN, OpenAPI, and OWASP documentation portals.

---

### Prompt 8: Six-Slide Capstone Presentation Synthesis
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Condense the entire project into an impactful six-slide presentation outline for faculty evaluation.
- **Prompt:**
  ```text
  Create an executive six-slide presentation for a third-year CSE college demonstration of Capstone 48.
  Slide 1: Title, problem statement, team roles.
  Slide 2: REST architectural principles & authoritative standards.
  Slide 3: System architecture, tech stack & database schema.
  Slide 4: RESTful endpoint design, HTTP status codes & versioning.
  Slide 5: Implementation demo, Swagger UI, automated pytest results.
  Slide 6: Empirical results, ethical AI considerations, future roadmap.
  For each slide, include Slide Title, Concise Bullets, Suggested Visual, and Speaker Notes.
  ```
- **Expected Output:** Markdown slides and outline tailored for a 10-minute faculty viva presentation.
- **Verification Method:** Peer rehearsal against the 10-minute presentation rubric.

---

### Prompt 9: Viva Voce & Technical Quiz Generation
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Formulate rigorous viva questions and multiple-choice questions testing core REST fundamentals.
- **Prompt:**
  ```text
  Generate 15 realistic faculty viva questions and a 10-question student quiz (with answer key) for the REST API kit.
  Cover:
  - Idempotency of PUT vs PATCH vs POST.
  - Differences between 200, 201, and 204.
  - Distinction between 400 Bad Request and 422 Unprocessable Content.
  - Why in-memory SQLite isolation is necessary during pytest runs.
  - How OpenAPI reflection eliminates documentation drift.
  - Ethical limits and hallucination risks of AI code generation.
  Provide clear, concise answers aligned exactly with our Python implementation.
  ```
- **Expected Output:** `viva_questions.md`, `quiz.md`, and `answer_key.md`.
- **Verification Method:** Faculty alignment check and cross-reference with implemented code.

---

### Prompt 10: Responsible AI, Privacy & Security Audit
- **Status:** `[EXECUTED IN PROJECT]`
- **Purpose:** Audit the project for hardcoded secrets, PII leakage, and overreaching claims.
- **Prompt:**
  ```text
  Analyze the current repository for ethical, privacy, and security risks:
  1. Are any real student names, emails, or student IDs present in seed data?
  2. Are any passwords, API tokens, or private keys committed to Git?
  3. Does the application leak database internal details on uncaught exceptions?
  4. Are any claims made regarding production-grade security without verification?
  Document findings in docs/ethics_and_limitations.md.
  ```
- **Expected Output:** Structured security and ethics audit report.
- **Verification Method:** Git repository grep audit (`git grep -i "key"`, `git grep -i "secret"`), inspecting `.gitignore` and `.env.example`.
