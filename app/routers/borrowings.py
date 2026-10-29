"""
Borrowing operations router providing borrowing creation, return handling,
and historical borrowing audit logs with transaction isolation and inventory safety.
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_db
from app.models import Book, Borrowing
from app.schemas import (
    BorrowRequest,
    ReturnRequest,
    BorrowingRead,
    PaginatedBorrowings,
    ErrorEnvelope,
)
from app.exceptions import (
    ResourceNotFoundException,
    ResourceConflictException,
    BadRequestException,
)
from app.config import get_settings

router = APIRouter(tags=["Borrowing"])
settings = get_settings()


@router.post(
    "/api/v1/books/{book_id}/borrow",
    response_model=BorrowingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow Book",
    description=(
        "Borrow a single copy of a book. Atomically checks availability and decrements available inventory. "
        "Returns 409 Conflict if no copies are available."
    ),
    responses={
        201: {"description": "Borrowing transaction created successfully.", "model": BorrowingRead},
        404: {"description": "Book not found.", "model": ErrorEnvelope},
        409: {"description": "Conflict: No copies of this book are currently available.", "model": ErrorEnvelope},
        422: {"description": "Validation error on parameters or payload.", "model": ErrorEnvelope},
    },
)
def borrow_book(
    book_id: int = Path(..., ge=1, description="Unique integer ID of the book to borrow."),
    payload: Optional[BorrowRequest] = None,
    db: Session = Depends(get_db),
) -> BorrowingRead:
    """Borrow an available book copy."""
    # Find book with row lock / transaction
    book = db.get(Book, book_id)
    if not book:
        raise ResourceNotFoundException(
            message=f"Book with ID {book_id} was not found.",
            code="BOOK_NOT_FOUND",
        )

    # Concurrency and inventory check
    if book.available_copies <= 0:
        raise ResourceConflictException(
            message=f"No copies of '{book.title}' are currently available (0 of {book.total_copies} available).",
            code="NO_COPIES_AVAILABLE",
        )

    borrower = (payload.borrower_name if payload and payload.borrower_name else settings.demo_borrower_name).strip()

    # Decrement available copies
    book.available_copies -= 1

    borrowing = Borrowing(
        book_id=book.id,
        borrower_name=borrower,
        borrowed_at=datetime.now(timezone.utc),
        status="BORROWED",
    )

    try:
        db.add(borrowing)
        db.commit()
        db.refresh(borrowing)

        read_dto = BorrowingRead.model_validate(borrowing)
        read_dto.book_title = book.title
        return read_dto
    except Exception:
        db.rollback()
        raise


@router.post(
    "/api/v1/books/{book_id}/return",
    response_model=BorrowingRead,
    status_code=status.HTTP_200_OK,
    summary="Return Borrowed Book",
    description=(
        "Return a borrowed copy of a book. Restores available inventory and updates the borrowing record. "
        "Allows supplying a specific borrowing_id or defaults to the most recent active borrowing."
    ),
    responses={
        200: {"description": "Book returned successfully.", "model": BorrowingRead},
        400: {"description": "Bad Request: Invalid return attempt or inventory overflow.", "model": ErrorEnvelope},
        404: {"description": "Not Found: Book or active borrowing record not found.", "model": ErrorEnvelope},
        422: {"description": "Validation error on parameters or payload.", "model": ErrorEnvelope},
    },
)
def return_book(
    book_id: int = Path(..., ge=1, description="Unique integer ID of the book being returned."),
    payload: Optional[ReturnRequest] = None,
    db: Session = Depends(get_db),
) -> BorrowingRead:
    """Return a previously borrowed book copy."""
    book = db.get(Book, book_id)
    if not book:
        raise ResourceNotFoundException(
            message=f"Book with ID {book_id} was not found.",
            code="BOOK_NOT_FOUND",
        )

    # Find the target active borrowing record
    query = select(Borrowing).where(Borrowing.book_id == book_id, Borrowing.status == "BORROWED")

    if payload and payload.borrowing_id:
        query = query.where(Borrowing.id == payload.borrowing_id)

    # Order by oldest active borrowing if not specified
    query = query.order_by(Borrowing.borrowed_at.asc())
    borrowing = db.scalars(query).first()

    if not borrowing:
        if payload and payload.borrowing_id:
            raise ResourceNotFoundException(
                message=f"Active borrowing record #{payload.borrowing_id} for book ID {book_id} was not found.",
                code="NO_ACTIVE_BORROWING",
            )
        raise ResourceNotFoundException(
            message=f"No active borrowing records found for book '{book.title}' (ID {book_id}).",
            code="NO_ACTIVE_BORROWING",
        )

    # Prevent invalid return overflow
    if book.available_copies >= book.total_copies:
        raise BadRequestException(
            message=f"All copies of '{book.title}' are already in inventory ({book.available_copies}/{book.total_copies}).",
            code="INVENTORY_OVERFLOW",
        )

    # Mark returned and increment available copies
    borrowing.status = "RETURNED"
    borrowing.returned_at = datetime.now(timezone.utc)
    book.available_copies += 1

    try:
        db.commit()
        db.refresh(borrowing)

        read_dto = BorrowingRead.model_validate(borrowing)
        read_dto.book_title = book.title
        return read_dto
    except Exception:
        db.rollback()
        raise


@router.get(
    "/api/v1/borrowings",
    response_model=PaginatedBorrowings,
    status_code=status.HTTP_200_OK,
    summary="List Borrowing Records",
    description="Retrieve historical borrowing audit logs with pagination and optional filtering by status or book ID.",
    responses={
        200: {"description": "A paginated list of borrowing records.", "model": PaginatedBorrowings},
        422: {"description": "Validation error on query parameters.", "model": ErrorEnvelope},
    },
)
def list_borrowings(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of records to return (1-100)."),
    offset: int = Query(default=0, ge=0, description="Offset index for pagination."),
    status: Optional[str] = Query(default=None, pattern=r"^(BORROWED|RETURNED)$", description="Filter by status: BORROWED or RETURNED."),
    book_id: Optional[int] = Query(default=None, ge=1, description="Filter by specific book ID."),
    db: Session = Depends(get_db),
) -> PaginatedBorrowings:
    """List borrowing audit records with pagination and filters."""
    query = select(Borrowing)

    if status:
        query = query.where(Borrowing.status == status)
    if book_id:
        query = query.where(Borrowing.book_id == book_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Paginate and order by newest first
    paginated_query = query.order_by(Borrowing.id.desc()).offset(offset).limit(limit)
    borrowings = db.scalars(paginated_query).all()

    items = []
    for b in borrowings:
        dto = BorrowingRead.model_validate(b)
        dto.book_title = b.book.title if b.book else None
        items.append(dto)

    return PaginatedBorrowings(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
