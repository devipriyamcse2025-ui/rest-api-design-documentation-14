"""
Main FastAPI Application Entrypoint.
Configures middleware, routers, exception handlers, lifecycle events, and OpenAPI metadata.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, SessionLocal
from app.exceptions import AppException
from app.routers import health, books, borrowings
from app.models import Book

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rest-api-kit")

settings = get_settings()

tags_metadata = [
    {
        "name": "Health",
        "description": "System health, versioning, and database reachability probes.",
    },
    {
        "name": "Books",
        "description": "Inventory management: list, retrieve, create, replace, patch, and delete books.",
    },
    {
        "name": "Borrowing",
        "description": "Library lending workflow: borrow book copies, return copies, and inspect audit logs.",
    },
]


def seed_demo_data_if_empty() -> None:
    """Safely seed initial demonstration books if database is empty."""
    db = SessionLocal()
    try:
        existing_count = db.query(Book).count()
        if existing_count == 0:
            logger.info("Database is empty. Seeding initial demonstration books...")
            demo_books = [
                Book(
                    title="Clean Code: A Handbook of Agile Software Craftsmanship",
                    author="Robert C. Martin",
                    isbn="978-0132350884",
                    publication_year=2008,
                    total_copies=4,
                    available_copies=4,
                ),
                Book(
                    title="Designing Data-Intensive Applications",
                    author="Martin Kleppmann",
                    isbn="978-1449373320",
                    publication_year=2017,
                    total_copies=5,
                    available_copies=5,
                ),
                Book(
                    title="Design Patterns: Elements of Reusable Object-Oriented Software",
                    author="Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
                    isbn="978-0201633610",
                    publication_year=1994,
                    total_copies=3,
                    available_copies=3,
                ),
                Book(
                    title="Computer Networking: A Top-Down Approach",
                    author="James Kurose, Keith Ross",
                    isbn="978-0133594140",
                    publication_year=2021,
                    total_copies=6,
                    available_copies=6,
                ),
                Book(
                    title="Introduction to Algorithms (CLRS)",
                    author="Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
                    isbn="978-0262046305",
                    publication_year=2022,
                    total_copies=2,
                    available_copies=2,
                ),
            ]
            db.add_all(demo_books)
            db.commit()
            logger.info("Successfully seeded %d demonstration books.", len(demo_books))
    except Exception as exc:
        db.rollback()
        logger.error("Failed to seed initial demonstration data: %s", exc)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing database schema...")
    init_db()
    seed_demo_data_if_empty()
    logger.info("Application startup complete. Ready to receive requests.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration for browser clients and local developer tooling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Centralized Error Handlers
# ---------------------------------------------------------

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle domain-specific application exceptions with standardized schema."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Intercept FastAPI/Pydantic validation errors and format into standard error envelope."""
    details = []
    for err in exc.errors():
        details.append(
            {
                "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            }
        )

    # HTTP 422 Unprocessable Content (RFC 9110)
    status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request payload or parameters failed schema validation.",
                "details": details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled runtime errors safely without leaking internal stack traces."""
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred. Please contact the administrator.",
                "details": None,
            }
        },
    )


# ---------------------------------------------------------
# Routers Registration
# ---------------------------------------------------------

app.include_router(health.router)
app.include_router(books.router)
app.include_router(borrowings.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Root Welcome & Navigation Index",
    description="Provides quick navigation links to interactive documentation and endpoints.",
)
def root_index():
    """Welcoming landing page with links to docs."""
    return {
        "message": f"Welcome to the {settings.app_name} (v{settings.app_version})",
        "interactive_docs": "/docs",
        "redoc_docs": "/redoc",
        "openapi_spec": "/openapi.json",
        "health_check": "/health",
        "api_v1_books": "/api/v1/books",
        "api_v1_borrowings": "/api/v1/borrowings",
    }
