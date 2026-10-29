"""
Custom domain exception hierarchy for standardized REST API error responses.
Ensures every exception carries an HTTP status code, machine-readable code,
and informative human-readable message.
"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for application-level errors."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class ResourceNotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.", code: str = "RESOURCE_NOT_FOUND", details: Any = None):
        super().__init__(status_code=404, code=code, message=message, details=details)


class ResourceConflictException(AppException):
    def __init__(self, message: str, code: str = "CONFLICT", details: Any = None):
        super().__init__(status_code=409, code=code, message=message, details=details)


class BadRequestException(AppException):
    def __init__(self, message: str, code: str = "BAD_REQUEST", details: Any = None):
        super().__init__(status_code=400, code=code, message=message, details=details)
