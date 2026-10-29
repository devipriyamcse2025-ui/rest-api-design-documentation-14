"""
Book management router providing complete CRUD operations with pagination,
search filtering, strict validation, transaction safety, and standard HTTP responses.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, select, func

from app.database import get_db
from app.models import Book, Borrowing
from app.schemas import (
    BookCreate,
    BookUpdate,
    BookPatch,
    BookRead,
    PaginatedBooks,
    ErrorEnvelope,
)
from app.exceptions import (
    ResourceNotFoundException,
    ResourceConflictException,
    BadRequestException,
)
from app.config import get_settings

router = APIRouter(prefix="/api/v1/books", tags=["Books"])
settings = get_settings()


@router.get(
    "",
    response_model=PaginatedBooks,
    status_code=status.HTTP_200_OK,
    summary="List Books",
    description="Retrieve a paginated collection of books. Supports optional case-insensitive substring search on title and author.",
    responses={
        200: {"description": "A paginated list of books.", "model": PaginatedBooks},
        422: {"description": "Validation error on query parameters.", "model": ErrorEnvelope},
    },
)
def list_books(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of books to return (1-100)."),
    offset: int = Query(default=0, ge=0, description="Offset index for pagination."),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Filter by title or author."),
    db: Session = Depends(get_db),
) -> PaginatedBooks:
    """List books with pagination and optional search."""
    query = select(Book)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.where(
            or_(
                Book.title.ilike(search_filter),
                Book.author.ilike(search_filter),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Apply pagination and sorting
    paginated_query = query.order_by(Book.id.asc()).offset(offset).limit(limit)
    items = db.scalars(paginated_query).all()

    return PaginatedBooks(
        items=[BookRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{book_id}",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
    summary="Get Book by ID",
    description="Retrieve a single book resource by its unique primary key identifier.",
    responses={
        200: {"description": "The requested book was found.", "model": BookRead},
        404: {"description": "Book not found.", "model": ErrorEnvelope},
        422: {"description": "Validation error on book_id path parameter.", "model": ErrorEnvelope},
    },
)
def get_book(
    book_id: int = Path(..., ge=1, description="Unique integer ID of the book."),
    db: Session = Depends(get_db),
) -> BookRead:
    """Retrieve an existing book by ID."""
    book = db.get(Book, book_id)
    if not book:
        raise ResourceNotFoundException(
            message=f"Book with ID {book_id} was not found.",
            code="BOOK_NOT_FOUND",
        )
    return BookRead.model_validate(book)


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Book",
    description="Add a new book to the library inventory. ISBN must be unique across all records.",
    responses={
        201: {"description": "Book successfully created.", "model": BookRead},
        409: {"description": "Conflict: A book with this ISBN already exists.", "model": ErrorEnvelope},
        422: {"description": "Validation error on request body.", "model": ErrorEnvelope},
    },
)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
) -> BookRead:
    """Create a new book record."""
    # Check ISBN uniqueness
    existing = db.scalar(select(Book).where(Book.isbn == book_in.isbn))
    if existing:
        raise ResourceConflictException(
            message=f"A book with ISBN '{book_in.isbn}' already exists (ID: {existing.id}).",
            code="DUPLICATE_ISBN",
        )

    book = Book(
        title=book_in.title,
        author=book_in.author,
        isbn=book_in.isbn,
        publication_year=book_in.publication_year,
        total_copies=book_in.total_copies,
        available_copies=book_in.total_copies,  # Newly created book starts with all copies available
    )
    try:
        db.add(book)
        db.commit()
        db.refresh(book)
        return BookRead.model_validate(book)
    except Exception:
        db.rollback()
        raise


@router.put(
    "/{book_id}",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
    summary="Replace Book (Complete Update)",
    description="Completely replace an existing book's metadata. All attributes must be provided.",
    responses={
        200: {"description": "Book successfully replaced.", "model": BookRead},
        400: {"description": "Bad Request: Total copies cannot be lower than currently borrowed count.", "model": ErrorEnvelope},
        404: {"description": "Book not found.", "model": ErrorEnvelope},
        409: {"description": "Conflict: Updated ISBN conflicts with another book.", "model": ErrorEnvelope},
        422: {"description": "Validation error on request body or parameters.", "model": ErrorEnvelope},
    },
)
def replace_book(
    book_in: BookUpdate,
    book_id: int = Path(..., ge=1, description="Unique integer ID of the book."),
    db: Session = Depends(get_db),
) -> BookRead:
    """Full update / replacement of an existing book."""
    book = db.get(Book, book_id)
    if not book:
        raise ResourceNotFoundException(
            message=f"Book with ID {book_id} was not found.",
            code="BOOK_NOT_FOUND",
        )

    # Check ISBN uniqueness against other books
    if book_in.isbn != book.isbn:
        conflict = db.scalar(select(Book).where(Book.isbn == book_in.isbn, Book.id != book_id))
        if conflict:
            raise ResourceConflictException(
                message=f"Another book with ISBN '{book_in.isbn}' already exists (ID: {conflict.id}).",
                code="DUPLICATE_ISBN",
            )

    # Validate inventory adjustments against active borrowings
    borrowed_count = book.total_copies - book.available_copies
    if book_in.total_copies < borrowed_count:
        raise BadRequestException(
            message=(
                f"Cannot reduce total_copies to {book_in.total_copies}. "
                f"There are currently {borrowed_count} active borrowed copies."
            ),
            code="INVALID_COPY_REDUCTION",
        )

    # Update attributes
    book.title = book_in.title
    book.author = book_in.author
    book.isbn = book_in.isbn
    book.publication_year = book_in.publication_year
    book.total_copies = book_in.total_copies
    book.available_copies = book_in.total_copies - borrowed_count

    try:
        db.commit()
        db.refresh(book)
        return BookRead.model_validate(book)
    except Exception:
        db.rollback()
        raise


@router.patch(
    "/{book_id}",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
    summary="Partially Update Book",
    description="Update one or more fields of an existing book. Omitted fields remain unchanged.",
    responses={
        200: {"description": "Book successfully updated.", "model": BookRead},
        400: {"description": "Bad Request: Updated total copies is less than active borrowings.", "model": ErrorEnvelope},
        404: {"description": "Book not found.", "model": ErrorEnvelope},
        409: {"description": "Conflict: Updated ISBN conflicts with another book.", "model": ErrorEnvelope},
        422: {"description": "Validation error on request body or parameters.", "model": ErrorEnvelope},
    },
)
def patch_book(
    book_in: BookPatch,
    book_id: int = Path(..., ge=1, description="Unique integer ID of the book."),
    db: Session = Depends(get_db),
) -> BookRead:
    """Partial update of an existing book."""
    book = db.get(Book, book_id)
    if not book:
        raise ResourceNotFoundException(
            message=f"Book with ID {book_id} was not found.",
            code="BOOK_NOT_FOUND",
        )

    patch_data = book_in.model_dump(exclude_unset=True)
    if not patch_data:
        return BookRead.model_validate(book)

    # Check ISBN uniqueness if changed
    if "isbn" in patch_data and patch_data["isbn"] != book.isbn:
        conflict = db.scalar(select(Book).where(Book.isbn == patch_data["isbn"], Book.id != book_id))
        if conflict:
            raise ResourceConflictException(
                message=f"Another book with ISBN '{patch_data['isbn']}' already exists (ID: {conflict.id}).",
                code="DUPLICATE_ISBN",
            )
        book.isbn = patch_data["isbn"]

    # Check total_copies if changed
    if "total_copies" in patch_data:
        new_total = patch_data["total_copies"]
        borrowed_count = book.total_copies - book.available_copies
        if new_total < borrowed_count:
            raise BadRequestException(
                message=(
                    f"Cannot reduce total_copies to {new_total}. "
                    f"There are currently {borrowed_count} active borrowed copies."
                ),
                code="INVALID_COPY_REDUCTION",
            )
        book.total_copies = new_total
        book.available_copies = new_total - borrowed_count

    if "title" in patch_data:
        book.title = patch_data["title"]
    if "author" in patch_data:
        book.author = patch_data["author"]
    if "publication_year" in patch_data:
        book.publication_year = patch_data["publication_year"]

    try:
        db.commit()
        db.refresh(book)
        return BookRead.model_validate(book)
    except Exception:
        db.rollback()
        raise


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Book",
    description=(
        "Permanently delete a book from the library. "
        "Deletion is rejected with 409 Conflict if active borrowings exist for this book."
    ),
    responses={
        204: {"description": "Book successfully deleted. No response body returned."},
        404: {"description": "Book not found.", "model": ErrorEnvelope},
        409: {"description": "Conflict: Active borrowings exist for this book.", "model": ErrorEnvelope},
        422: {"description": "Validation error on book_id path parameter.", "model": ErrorEnvelope},
    },
)
def delete_book(
    book_id: int = Path(..., ge=1, description="Unique integer ID of the book."),
    db: Session = Depends(get_db),
) -> Response:
    """Delete a book, enforcing business policy regarding active borrowings."""
    book = db.get(Book, book_id)
    if not book:
        raise ResourceNotFoundException(
            message=f"Book with ID {book_id} was not found.",
            code="BOOK_NOT_FOUND",
        )

    # Check for active borrowings
    active_borrowings = db.scalar(
        select(func.count()).select_from(Borrowing).where(
            Borrowing.book_id == book_id,
            Borrowing.status == "BORROWED",
        )
    ) or 0

    if active_borrowings > 0:
        raise ResourceConflictException(
            message=(
                f"Cannot delete book with ID {book_id}. "
                f"There are {active_borrowings} active borrowing records. "
                "All borrowed copies must be returned before deleting the book."
            ),
            code="ACTIVE_BORROWINGS_EXIST",
        )

    try:
        db.delete(book)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception:
        db.rollback()
        raise
