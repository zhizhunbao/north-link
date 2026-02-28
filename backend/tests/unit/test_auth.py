"""Unit tests for JWT auth utilities."""

import pytest

from app.core.auth import create_access_token, create_refresh_token, verify_token


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token_returns_string(self):
        token = create_access_token("user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(self):
        token = create_refresh_token("user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_access_token(self):
        token = create_access_token("user-456")
        user_id = verify_token(token, expected_type="access")
        assert user_id == "user-456"

    def test_verify_valid_refresh_token(self):
        token = create_refresh_token("user-789")
        user_id = verify_token(token, expected_type="refresh")
        assert user_id == "user-789"

    def test_access_token_fails_for_refresh_type(self):
        token = create_access_token("user-123")
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            verify_token(token, expected_type="refresh")

    def test_refresh_token_fails_for_access_type(self):
        token = create_refresh_token("user-123")
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            verify_token(token, expected_type="access")

    def test_invalid_token_raises_exception(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            verify_token("invalid-token-string", expected_type="access")

    def test_different_users_get_different_tokens(self):
        token1 = create_access_token("user-a")
        token2 = create_access_token("user-b")
        assert token1 != token2
