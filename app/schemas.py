"""
Pydantic schemas for request validation, response serialization, and documentation.
Enforces strict typing, sensible constraints, and informative error structures.
"""

from datetime import datetime, timezone
from typing import List, Optional, Any
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ---------------------------------------------------------
# Unified Error Schemas
# ---------------------------------------------------------

class ErrorBody(BaseModel):
    code: str = Field(..., description="Machine-readable uppercase error code (e.g. BOOK_NOT_FOUND)")
    message: str = Field(..., description="Human-readable explanation of what went wrong")
    details: Optional[Any] = Field(None, description="Optional detailed validation errors or diagnostic context")


class ErrorEnvelope(BaseModel):
    error: ErrorBody

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "BOOK_NOT_FOUND",
                    "message": "The requested book was not found.",
                    "details": None,
                }
            }
        }
    )


# ---------------------------------------------------------
# Book Schemas
# ---------------------------------------------------------

class BookBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Title of the book",
        examples=["Designing Data-Intensive Applications"],
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Primary author or contributors",
        examples=["Martin Kleppmann"],
    )
    isbn: str = Field(
        ...,
        min_length=10,
        max_length=20,
        description="International Standard Book Number (ISBN-10 or ISBN-13)",
        examples=["978-1449373320"],
    )
    publication_year: int = Field(
        ...,
        description="Calendar year of publication (between 1000 and current year)",
        examples=[2017],
    )
    total_copies: int = Field(
        1,
        ge=1,
        le=10000,
        description="Total inventory count for this book (minimum 1)",
        examples=[5],
    )

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        cleaned = re.sub(r"[-\s]", "", v.strip())
        if not (len(cleaned) == 10 or len(cleaned) == 13):
            raise ValueError("ISBN must be 10 or 13 digits (hyphens permitted).")
        if not re.match(r"^[0-9]{9}[0-9X]$", cleaned) and not re.match(r"^[0-9]{13}$", cleaned):
            raise ValueError("ISBN format is invalid. Must contain valid numeric digits or terminal 'X' for ISBN-10.")
        return v.strip()

    @field_validator("publication_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now(timezone.utc).year
        if v < 1000 or v > current_year:
            raise ValueError(f"publication_year must be between 1000 and {current_year}.")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    """Schema for complete resource replacement (PUT)."""
    pass


class BookPatch(BaseModel):
    """Schema for partial resource update (PATCH). All fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    publication_year: Optional[int] = None
    total_copies: Optional[int] = Field(None, ge=1, le=10000)

    @field_validator("isbn")
    @classmethod
    def validate_patch_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = re.sub(r"[-\s]", "", v.strip())
        if not (len(cleaned) == 10 or len(cleaned) == 13):
            raise ValueError("ISBN must be 10 or 13 digits (hyphens permitted).")
        if not re.match(r"^[0-9]{9}[0-9X]$", cleaned) and not re.match(r"^[0-9]{13}$", cleaned):
            raise ValueError("ISBN format is invalid.")
        return v.strip()

    @field_validator("publication_year")
    @classmethod
    def validate_patch_year(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return None
        current_year = datetime.now(timezone.utc).year
        if v < 1000 or v > current_year:
            raise ValueError(f"publication_year must be between 1000 and {current_year}.")
        return v


class BookRead(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedBooks(BaseModel):
    items: List[BookRead]
    total: int = Field(..., description="Total matching books in inventory")
    limit: int = Field(..., description="Pagination page size")
    offset: int = Field(..., description="Pagination offset from start")


# ---------------------------------------------------------
# Borrowing Schemas
# ---------------------------------------------------------

class BorrowRequest(BaseModel):
    borrower_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Name or student ID of the borrower. Defaults to demo student if omitted.",
        examples=["Alex Johnson (Student ID: CS-301)"],
    )


class ReturnRequest(BaseModel):
    borrowing_id: Optional[int] = Field(
        None,
        description="Optional specific borrowing ID. If omitted, the latest active record for this book is returned.",
        examples=[1],
    )


class BorrowingRead(BaseModel):
    id: int
    book_id: int
    borrower_name: str
    borrowed_at: datetime
    returned_at: Optional[datetime] = None
    status: str
    book_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedBorrowings(BaseModel):
    items: List[BorrowingRead]
    total: int = Field(..., description="Total matching borrowing transactions")
    limit: int = Field(..., description="Pagination limit")
    offset: int = Field(..., description="Pagination offset")


# ---------------------------------------------------------
# Health Check Schema
# ---------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = Field("healthy", examples=["healthy"])
    version: str = Field(..., examples=["1.0.0"])
    timestamp: datetime
    database: str = Field(..., examples=["connected"])
