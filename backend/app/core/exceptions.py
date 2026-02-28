"""Custom exception classes and unified error handlers."""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception with error code."""

    def __init__(self, status_code: int, detail: str, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=f"{resource.upper()}_NOT_FOUND",
        )


class DuplicateException(AppException):
    """Resource already exists (409)."""

    def __init__(self, resource: str, field: str = ""):
        detail = f"{resource} already exists"
        if field:
            detail = f"{resource} with this {field} already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code=f"{resource.upper()}_DUPLICATE",
        )


class ValidationException(AppException):
    """Business validation error (422)."""

    def __init__(self, detail: str, code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
        )


class AuthenticationException(AppException):
    """Authentication failed (401)."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="AUTH_FAILED",
        )
