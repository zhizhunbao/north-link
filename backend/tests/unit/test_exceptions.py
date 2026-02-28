"""Unit tests for custom exception classes."""

import pytest
from fastapi import status

from app.core.exceptions import (
    AppException,
    AuthenticationException,
    DuplicateException,
    NotFoundException,
    ValidationException,
)


class TestNotFoundException:
    """Test NotFoundException behavior."""

    def test_basic_not_found(self):
        exc = NotFoundException("Product")
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "Product not found" in exc.detail
        assert exc.code == "PRODUCT_NOT_FOUND"

    def test_not_found_with_identifier(self):
        exc = NotFoundException("User", "abc-123")
        assert "User 'abc-123' not found" in exc.detail

    def test_inherits_from_app_exception(self):
        exc = NotFoundException("Order")
        assert isinstance(exc, AppException)


class TestDuplicateException:
    """Test DuplicateException behavior."""

    def test_basic_duplicate(self):
        exc = DuplicateException("Merchant")
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert "Merchant already exists" in exc.detail

    def test_duplicate_with_field(self):
        exc = DuplicateException("User", "email")
        assert "User with this email already exists" in exc.detail
        assert exc.code == "USER_DUPLICATE"


class TestValidationException:
    """Test ValidationException behavior."""

    def test_validation_error(self):
        exc = ValidationException("Price must be positive")
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.detail == "Price must be positive"
        assert exc.code == "VALIDATION_ERROR"

    def test_custom_code(self):
        exc = ValidationException("Invalid status", code="INVALID_STATUS")
        assert exc.code == "INVALID_STATUS"


class TestAuthenticationException:
    """Test AuthenticationException behavior."""

    def test_default_message(self):
        exc = AuthenticationException()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.code == "AUTH_FAILED"

    def test_custom_message(self):
        exc = AuthenticationException("账号已被禁用")
        assert exc.detail == "账号已被禁用"
