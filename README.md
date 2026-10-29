# REST API Design and Documentation Kit
**Capstone 48: Computer Science & Engineering Undergraduate Project**  
*How can AI help design, test, and document a clean REST API for a small application?*

---

## 1. Project Overview
The **REST API Design and Documentation Kit** is a comprehensive, production-grade educational reference implementation designed for third-year Computer Science Engineering students. It demonstrates how to architect, validate, test, document, and verify a clean RESTful web API for a Library Management system using modern Python backend technologies.

### Key Highlights
- **Framework:** FastAPI with high-performance ASGI architecture.
- **Relational Persistence:** SQLite database with SQLAlchemy 2.0 ORM and transaction guarantees.
- **Strict Data Validation:** Pydantic v2 schemas validating ISBNs, publication years, and positive copy counts.
- **Zero Documentation Drift:** Real-time OpenAPI 3.1.0 JSON schema reflection and embedded interactive Swagger UI (`/docs`) & ReDoc (`/redoc`).
- **Standardized Error Architecture:** Unified error responses `{ "error": { "code", "message", "details" } }` with RFC 9110 HTTP status codes (`200`, `201`, `204`, `400`, `404`, `409`, `422`, `500`).
- **Comprehensive Automated Testing:** 22 automated Pytest integration tests running against an isolated database with 100% pass rate.
- **CI/CD Route Linter:** Standalone documentation consistency automation script (`scripts/check_documentation.py`).
- **100% Free & Open-Source:** Zero paid APIs, zero external AI keys, and zero cloud subscriptions required.

---

## 2. Architecture & Layered Design
The kit follows a Clean Architecture design separating presentation, business logic, validation, and persistence:

```
rest-api/
│
├── app/                            # Application Core
│   ├── __init__.py                 # Package versioning metadata
│   ├── config.py                   # Central settings management & environment variables
│   ├── database.py                 # SQLite engine, sessionmaker & connection checks
│   ├── exceptions.py               # Domain exception hierarchy (404, 409, 400)
│   ├── models.py                   # SQLAlchemy ORM entities (Book, Borrowing)
│   ├── schemas.py                  # Pydantic v2 request/response DTOs & validators
│   ├── main.py                     # FastAPI application, lifecycle, middleware, error handlers
│   └── routers/                    # Route controllers
│       ├── __init__.py
│       ├── health.py               # GET /health probe & GET / root index
│       ├── books.py                # CRUD /api/v1/books with pagination & search
│       └── borrowings.py           # /api/v1/books/{id}/borrow, return, audit log
│
├── tests/                          # Automated Pytest Suite (100% Pass)
│   ├── __init__.py
│   ├── conftest.py                 # Isolated test database fixtures & TestClient setup
│   ├── test_health.py              # Health probe tests
│   ├── test_books.py               # Book CRUD, validation & pagination tests
│   ├── test_borrowings.py          # Concurrency boundary, loan & return tests
│   └── test_errors.py              # Unified error envelope & OpenAPI consistency tests
│
├── scripts/                        # Automation & Verification Utilities
│   ├── seed_database.py            # Idempotent database populator with demo books
│   ├── generate_openapi.py         # Static openapi.json generator directly from AST
│   ├── check_documentation.py      # Automation linter verifying OpenAPI route consistency
│   ├── verify_endpoints.py         # End-to-end live / in-process HTTP verifier
│   └── generate_verification_report.py # Benchmarking & actual test report builder
│
├── docs/                           # Capstone Reports & Guides
│   ├── research_report.md          # Full academic paper with official citations
│   ├── api_design_checklist.md     # Architectural checklist with verified statuses
│   ├── endpoint_design.md          # Comprehensive endpoint table & JSON examples
│   ├── status_codes.md             # HTTP status semantics & error handling guide
│   ├── api_usage_examples.md       # cURL, PowerShell, and Python invocation examples
│   ├── automation_guide.md         # Documentation consistency checker guide
│   ├── verification_report.md      # Actual test execution results & system audit
│   ├── before_after_analysis.md    # Manual vs AI-assisted workflow analysis
│   ├── prompt_library.md           # 10 core engineering prompts & verification methods
│   ├── ethics_and_limitations.md   # Responsible AI, data privacy & security limits
│   └── viva_questions.md           # 15 faculty viva voce questions and answers
│
├── presentation/                   # Capstone Presentation Deliverables
│   ├── slides.md                   # Exactly six main demonstration slides
│   └── presentation_outline.md     # Detailed 10-minute faculty presentation script
│
├── quiz/                           # Examination Deliverables
│   ├── quiz.md                     # 10-question student assessment
│   └── answer_key.md               # Detailed explanations and solutions
│
├── openapi/                        # OpenAPI Specifications
│   └── openapi.json                # Generated machine-readable OpenAPI 3.1.0 specification
│
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git exclusion rules for clean repository
├── LICENSE                         # Permissive MIT Open Source License
├── requirements.txt                # Exact pinned Python dependencies
├── run.bat                         # Automated Windows one-click startup script
├── run.sh                          # Automated Linux/macOS one-click startup script
└── README.md                       # This file
```

---

## 3. Prerequisites
- **Operating System:** Windows 10/11, Linux (Ubuntu/Debian/Fedora), or macOS.
- **Python:** Python 3.11 or compatible version installed.
- **Git:** (Optional) for version control tracking.

---

## 4. Quick Start (One-Click Execution)

### On Windows (Recommended)
Simply double-click or run from PowerShell:
```cmd
run.bat
```
*`run.bat` automatically creates the `.venv` virtual environment if missing, installs dependencies, initializes and seeds the database idempotently, and launches the server on `http://127.0.0.1:8000`.*

### On Linux / macOS
```bash
chmod +x run.sh
./run.sh
```

---

## 5. Manual Step-by-Step Installation

If you prefer setting up the application step by step:

### Step 1: Create and Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Seed Database Idempotently
```bash
python scripts/seed_database.py
```

### Step 4: Start the Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 6. Accessing Interactive Documentation
Once the server is running, open your web browser to:
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Raw OpenAPI 3.1.0 JSON:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- **Health Check Probe:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 7. Running Automated Tests & Verification

### Run Pytest Automated Test Suite (22 Tests)
```bash
# Run all tests with verbose output
python -m pytest -v
```
*All 22 unit, boundary, and error tests execute in ~1 second using an isolated temporary test database session.*

### Run Automation Route & Documentation Consistency Linter
```bash
# Compares OpenAPI schema against required routes; returns exit code 0 on success
python scripts/check_documentation.py
```

### Run End-to-End Live / In-Process Endpoint Verifier
```bash
# Tests all 11 core endpoints with real request/response verification
python scripts/verify_endpoints.py
```

### Regenerate Verification Report
```bash
# Executes tests and builds docs/verification_report.md
python scripts/generate_verification_report.py
```

---

## 8. Master Endpoint Summary Table

| Method | Endpoint URI | Description | Status Code |
|--------|--------------|-------------|-------------|
| `GET` | `/health` | Health check probe & database reachability | `200 OK` |
| `GET` | `/` | Root welcoming index with docs links | `200 OK` |
| `GET` | `/api/v1/books` | List books with pagination (`limit`, `offset`, `search`) | `200 OK` |
| `GET` | `/api/v1/books/{id}` | Retrieve single book by unique ID | `200 OK` / `404` |
| `POST` | `/api/v1/books` | Create a new book in inventory | `201 Created` / `409` |
| `PUT` | `/api/v1/books/{id}` | Complete replacement of book attributes | `200 OK` / `400` / `404` |
| `PATCH`| `/api/v1/books/{id}` | Partial update of book attributes | `200 OK` / `400` / `404` |
| `DELETE`| `/api/v1/books/{id}` | Permanently delete book (if no active loans) | `204 No Content` / `409` |
| `POST` | `/api/v1/books/{id}/borrow` | Borrow an available copy of a book | `201 Created` / `409` |
| `POST` | `/api/v1/books/{id}/return` | Return a borrowed copy of a book | `200 OK` / `404` |
| `GET` | `/api/v1/borrowings` | List borrowing audit records with filters | `200 OK` |

---

## 9. Example API Request & Response

### Borrow a Book (`POST /api/v1/books/2/borrow`)
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/books/2/borrow" \
     -H "Content-Type: application/json" \
     -d '{"borrower_name": "Demo Student (ID: CS-301)"}'
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "book_id": 2,
  "borrower_name": "Demo Student (ID: CS-301)",
  "borrowed_at": "2026-10-29T12:00:00.123456Z",
  "returned_at": null,
  "status": "BORROWED",
  "book_title": "Designing Data-Intensive Applications"
}
```

### Unified Error Response Example (`409 Conflict`)
If no copies are available:
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

## 10. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `python: command not found` | Python not in Windows PATH | Install Python 3.11+ and check "Add Python to PATH" during setup. |
| `Port 8000 in use` | Another process is bound to 8000 | Specify a different port: `uvicorn app.main:app --port 8080`. |
| `Application Control policy blocked .pyd` | Windows SAC active in `Downloads/` | The project includes pure Python fallbacks for SQLAlchemy. |
| `test_library.db locked` | Previous test process didn't terminate | Close lingering background test processes and delete `test_library.db`. |

---

## 11. Known Limitations & Roadmap
1. **SQLite Concurrency:** SQLite uses database-level write locks. While ideal for desktop demonstrations and local development, high-throughput multi-user writes require migrating to PostgreSQL in v2.
2. **Authentication Layer:** Intentionally omitted from v1 to keep student focus on REST fundamentals without authentication noise. A complete OAuth2/JWT RBAC specification is architected in `docs/ethics_and_limitations.md` for v2.

---

## 12. Responsible AI Declaration
In accordance with ethical academic research practices:
- AI assistance was utilized under supervised engineering protocols for boilerplate scaffolding and documentation synthesis.
- 100% of generated code, schemas, and endpoints were verified using compiler checks, AST inspection, and the 22-case automated Pytest suite.
- All literature citations and test counts represent genuine, verified facts; zero numbers or citations were fabricated.
- Demonstration seed data uses synthetic student personas only; no personally identifiable information (PII) was collected or stored.

---

## 13. License
This project is open-source and released under the [MIT License](LICENSE).
