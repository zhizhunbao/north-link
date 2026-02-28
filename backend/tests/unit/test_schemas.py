"""Unit tests for auth schemas (Pydantic validation)."""

import pytest
from pydantic import ValidationError

from app.modules.auth.schemas import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    UserResponse,
)


class TestLoginRequest:
    """Test LoginRequest validation."""

    def test_valid_login(self):
        req = LoginRequest(username="admin", password="secret123")
        assert req.username == "admin"
        assert req.password == "secret123"

    def test_short_password_fails(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="admin", password="123")

    def test_missing_fields_fails(self):
        with pytest.raises(ValidationError):
            LoginRequest()  # type: ignore


class TestPasswordChangeRequest:
    """Test PasswordChangeRequest validation."""

    def test_valid_change(self):
        req = PasswordChangeRequest(
            old_password="old123",
            new_password="new456",
        )
        assert req.old_password == "old123"
        assert req.new_password == "new456"


class TestTokenResponse:
    """Test TokenResponse construction."""

    def test_default_token_type(self):
        resp = TokenResponse(
            access_token="abc",
            refresh_token="def",
        )
        assert resp.token_type == "bearer"


class TestUserResponse:
    """Test UserResponse serialization."""

    def test_valid_user_response(self):
        import uuid
        from datetime import datetime

        resp = UserResponse(
            id=uuid.uuid4(),
            username="admin",
            role="admin",
            is_active=True,
            created_at=datetime.now(),
        )
        assert resp.username == "admin"
        assert resp.role == "admin"
