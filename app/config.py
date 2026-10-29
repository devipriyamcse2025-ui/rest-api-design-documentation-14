"""
Application configuration management using pydantic-settings / os environment.
Provides clean centralized settings with sensible defaults.
"""

import os
from functools import lru_cache
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "REST API Design and Documentation Kit"
    app_version: str = "1.0.0"
    app_description: str = (
        "Educational REST API demonstration kit for third-year CSE students. "
        "Demonstrates clean REST architecture, OpenAPI documentation, "
        "automated testing, and responsible AI-assisted engineering."
    )
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "true").lower() in ("true", "1", "yes"))
    
    server_host: str = Field(default_factory=lambda: os.getenv("SERVER_HOST", "127.0.0.1"))
    server_port: int = Field(default_factory=lambda: int(os.getenv("SERVER_PORT", "8000")))
    
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./library.db"))
    
    demo_borrower_name: str = Field(
        default_factory=lambda: os.getenv("DEMO_BORROWER_NAME", "Alex Johnson (Student ID: CS-301)")
    )
    default_page_limit: int = Field(default_factory=lambda: int(os.getenv("DEFAULT_PAGE_LIMIT", "10")))
    max_page_limit: int = Field(default_factory=lambda: int(os.getenv("MAX_PAGE_LIMIT", "100")))


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
