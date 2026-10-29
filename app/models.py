"""
SQLAlchemy database models for the Library Management system.
Includes Book and Borrowing entities with relationships and constraints.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=False, index=True)
    publication_year = Column(Integer, nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    borrowings = relationship("Borrowing", back_populates="book", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("total_copies >= 1", name="check_total_copies_positive"),
        CheckConstraint("available_copies >= 0", name="check_available_copies_non_negative"),
        CheckConstraint("available_copies <= total_copies", name="check_available_le_total"),
    )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title='{self.title}' isbn='{self.isbn}' available={self.available_copies}/{self.total_copies}>"


class Borrowing(Base):
    __tablename__ = "borrowings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True)
    borrower_name = Column(String(255), nullable=False)
    borrowed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="BORROWED", index=True)  # BORROWED or RETURNED

    # Relationships
    book = relationship("Book", back_populates="borrowings")

    def __repr__(self) -> str:
        return f"<Borrowing id={self.id} book_id={self.book_id} borrower='{self.borrower_name}' status='{self.status}'>"
