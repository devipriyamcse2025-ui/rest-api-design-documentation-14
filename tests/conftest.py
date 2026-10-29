"""
Pytest configuration and shared fixtures.
Configures an isolated temporary SQLite database to ensure tests never touch
the development or demonstration database.
"""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base, get_db
from app.main import app
from app.models import Book

TEST_DB_FILE = "./test_library.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def manage_test_db():
    """Ensure clean test database file before and after test session."""
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def clean_tables_each_test():
    """Wipe all rows before each test to guarantee absolute isolation."""
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    yield


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a direct database session for test fixture setup."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient configured with dependency overrides pointing to isolated test DB."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_book(db_session: Session) -> Book:
    """Fixture providing an existing seeded book for testing."""
    book = Book(
        title="Test-Driven Development by Example",
        author="Kent Beck",
        isbn="978-0321146533",
        publication_year=2002,
        total_copies=3,
        available_copies=3,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book
