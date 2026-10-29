"""
Database Seeding Script.
Safely populates demonstration books without creating duplicate records on repeated runs.
"""

import sys
import os

# Add root folder to sys.path so app modules are resolvable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db
from app.models import Book


DEMO_BOOKS = [
    {
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publication_year": 2008,
        "total_copies": 4,
        "available_copies": 4,
    },
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "isbn": "978-1449373320",
        "publication_year": 2017,
        "total_copies": 5,
        "available_copies": 5,
    },
    {
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "isbn": "978-0201633610",
        "publication_year": 1994,
        "total_copies": 3,
        "available_copies": 3,
    },
    {
        "title": "Computer Networking: A Top-Down Approach",
        "author": "James Kurose, Keith Ross",
        "isbn": "978-0133594140",
        "publication_year": 2021,
        "total_copies": 6,
        "available_copies": 6,
    },
    {
        "title": "Introduction to Algorithms (CLRS)",
        "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
        "isbn": "978-0262046305",
        "publication_year": 2022,
        "total_copies": 2,
        "available_copies": 2,
    },
    {
        "title": "Operating System Concepts",
        "author": "Abraham Silberschatz, Peter B. Galvin, Greg Gagne",
        "isbn": "978-1119800361",
        "publication_year": 2021,
        "total_copies": 4,
        "available_copies": 4,
    },
    {
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell, Peter Norvig",
        "isbn": "978-0134610993",
        "publication_year": 2020,
        "total_copies": 3,
        "available_copies": 3,
    },
]


def seed_database() -> int:
    """Idempotently seed books by checking ISBN existence."""
    print("Initializing database tables if not present...")
    init_db()

    db = SessionLocal()
    inserted_count = 0
    try:
        print("Checking existing library records...")
        for book_data in DEMO_BOOKS:
            existing = db.query(Book).filter(Book.isbn == book_data["isbn"]).first()
            if not existing:
                new_book = Book(**book_data)
                db.add(new_book)
                inserted_count += 1
                print(f" [+] Inserted: '{book_data['title']}' (ISBN: {book_data['isbn']})")
            else:
                print(f" [=] Already exists: '{book_data['title']}' (ID: {existing.id})")

        db.commit()
        total_books = db.query(Book).count()
        print(f"\nSeeding complete! Added {inserted_count} new books. Total inventory: {total_books} books.")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"\n[!] Error during database seeding: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(seed_database())
