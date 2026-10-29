# Responsible AI, Ethics, and Engineering Limitations Report
**Project:** REST API Design and Documentation Kit (Capstone 48)  
**Target Audience:** Third-Year Computer Science & Engineering Students & Faculty Evaluators  

---

## 1. Principles of Responsible AI Use in Engineering
Generative AI tools and Large Language Models (LLMs) have demonstrated substantial utility in modern software development. However, an engineering discipline requires that AI assistance be deployed under strict ethical boundaries and verification standards. The code and documentation in this repository adhere to the following core tenets:

### 1.1 Bugs in AI-Generated Code
AI models predict tokens based on statistical probabilities in training corpora; they do not possess execution environments or semantic understanding. Consequently, AI-generated code frequently contains:
- Subtle race conditions during concurrent database updates.
- Deprecated library methods (e.g. using deprecated Pydantic v1 syntax or obsolete Starlette status names).
- Incorrect status code mappings (e.g. defaulting to 200 OK when 201 Created or 204 No Content is mandated by RFC 9110).

**Our Safeguard:** No AI-generated code was committed without human review, static analysis, and verification via the 22-case automated pytest suite.

### 1.2 Hallucination of Citations and Research
A well-documented failure mode of generative AI is the fabrication of plausible-sounding URLs, paper titles, author names, or performance statistics.
**Our Safeguard:** All citations in `docs/research_report.md` were manually verified against live official repositories (MDN Web Docs, the OpenAPI 3.1.0 specification, FastAPI documentation, and OWASP). No citations or benchmark figures were fabricated.

### 1.3 Human Review and Developer Accountability
Software engineers bear legal and moral accountability for the behavior of systems they deploy. AI is an assistant; the human engineer is the author of record. In this project, all architectural decisions (such as requiring transactional rollbacks on inventory reduction and enforcing foreign key restrictions) reflect deliberate human design choices.

---

## 2. Privacy by Design & Data Ethics

### 2.1 Synthetic Data Only
To protect user privacy and comply with global data protection standards (GDPR, FERPA):
- The database contains **zero real student or user data**.
- Demonstration records utilize synthetic student personas (e.g. `"Alex Johnson (Student ID: CS-301)"`).
- Demonstration book records comprise standard, widely published computer science textbooks.

### 2.2 No API Keys or Secrets in Version Control
- The repository does not include production database credentials, API secret keys, or private tokens.
- Configuration is decoupled using environment variables loaded via `app/config.py`.
- The included `.env.example` file contains dummy placeholders only (`SERVER_HOST="127.0.0.1"`, `DATABASE_URL="sqlite:///./library.db"`).
- `.gitignore` explicitly prevents `.env`, SQLite `.db` binaries, and temporary virtual environments from ever being staged or committed.

---

## 3. Security Boundary & Vulnerability Analysis

### 3.1 Information Leakage & Exception Shielding
Insecure error handling (OWASP API8: Security Misconfiguration) occurs when applications return raw database error messages or Python stack traces to clients.
- In this project, an unhandled exception handler catches generic exceptions, logs the full diagnostic trace to internal server stdout, and emits a sanitized response to the HTTP client:
  ```json
  {
    "error": {
      "code": "INTERNAL_SERVER_ERROR",
      "message": "An unexpected internal server error occurred. Please contact the administrator.",
      "details": null
    }
  }
  ```

### 3.2 SQL Injection Prevention
SQL injection vulnerabilities are mitigated by employing SQLAlchemy ORM parameterized queries throughout the application. Dynamic user input from the search query parameter is safely passed through parameterized filters (`Book.title.ilike(f"%{search}%")`), preventing malicious SQL execution.

### 3.3 Transparent Statement on Authentication
**Explicit Limitation:** This Version 1.0.0 kit intentionally omits an authentication and authorization layer (such as JWT tokens or OAuth2).
- *Reasoning:* Adding a rudimentary or flawed authentication shim merely to claim the project is "secure" represents deceptive engineering. For third-year students learning REST fundamentals, coupling authentication complexity with basic HTTP CRUD mechanics often obscures core REST concepts.
- *Future Safeguard Roadmap (v2):*
  - Implementation of OAuth2 password flow with JWT bearer tokens.
  - Role-Based Access Control (RBAC) distinguishing between `Librarian` (CRUD on books) and `Student` (borrow/return permissions).
  - Rate limiting via Redis tokens to defend against brute-force denial of service.

---

## 4. Software Licensing & Open-Source Attribution
This project is released under the permissive **MIT License**, permitting educational reuse, modification, and demonstration.
All third-party dependencies are open-source and compatible with the MIT license:
- **FastAPI:** MIT License
- **Starlette:** BSD 3-Clause License
- **Pydantic:** MIT License
- **SQLAlchemy:** MIT License
- **Pytest:** MIT License
- **Uvicorn:** BSD 3-Clause License

---

## 5. Engineering Limitations Summary
1. **Single-Node Persistence:** Backed by SQLite. Not suitable for multi-region or high-concurrency write clusters.
2. **Local Loopback Requirement:** Interactive Swagger UI and live HTTP verification require local loopback networking permissions on the host system.
3. **Absence of SSL/TLS in Local Dev:** The development server runs over unencrypted HTTP (`http://127.0.0.1:8000`). Production deployments must be fronted by a reverse proxy (e.g. Nginx, Caddy) terminating HTTPS/TLS.
