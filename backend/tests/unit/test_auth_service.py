"""Unit tests for AuthService (mocked database)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import AuthenticationException, NotFoundException
from app.modules.auth.service import AuthService, pwd_context
from app.modules.auth.schemas import LoginRequest, PasswordChangeRequest


class TestAuthServiceAuthenticate:
    """Test AuthService.authenticate method."""

    @pytest.fixture
    def service(self, mock_db):
        return AuthService(mock_db)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock()
        user.id = "user-uuid-1"
        user.username = "admin"
        user.password_hash = pwd_context.hash("pass12")
        user.is_active = True
        user.last_login = None
        return user

    @pytest.mark.asyncio
    async def test_authenticate_success(self, service, mock_db, mock_user):
        # Arrange
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result_mock

        login_data = LoginRequest(
            username="admin",
            password="pass12",
        )

        # Act
        response = await service.authenticate(login_data)

        # Assert
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, service, mock_db, mock_user):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result_mock

        login_data = LoginRequest(
            username="admin",
            password="wrong1",
        )

        with pytest.raises(AuthenticationException, match="用户名或密码错误"):
            await service.authenticate(login_data)

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, service, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        login_data = LoginRequest(
            username="nonexistent",
            password="any123",
        )

        with pytest.raises(AuthenticationException):
            await service.authenticate(login_data)

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, service, mock_db, mock_user):
        mock_user.is_active = False
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result_mock

        login_data = LoginRequest(
            username="admin",
            password="pass12",
        )

        with pytest.raises(AuthenticationException, match="账号已被禁用"):
            await service.authenticate(login_data)


class TestAuthServiceChangePassword:
    """Test AuthService.change_password method."""

    @pytest.fixture
    def service(self, mock_db):
        return AuthService(mock_db)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock()
        user.id = "user-uuid-1"
        user.password_hash = pwd_context.hash("old123")
        return user

    @pytest.mark.asyncio
    async def test_change_password_success(self, service, mock_db, mock_user):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result_mock

        data = PasswordChangeRequest(
            old_password="old123",
            new_password="new456",
        )

        await service.change_password("user-uuid-1", data)
        # Password hash should be updated
        assert mock_user.password_hash != pwd_context.hash("old123")

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, service, mock_db, mock_user):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result_mock

        data = PasswordChangeRequest(
            old_password="wrong1",
            new_password="new456",
        )

        with pytest.raises(AuthenticationException, match="旧密码错误"):
            await service.change_password("user-uuid-1", data)

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, service, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        data = PasswordChangeRequest(
            old_password="old123",
            new_password="new456",
        )

        with pytest.raises(NotFoundException):
            await service.change_password("nonexistent-id", data)


class TestHashPassword:
    """Test static hash_password utility."""

    def test_hash_password_returns_bcrypt_hash(self):
        hashed = AuthService.hash_password("my-password")
        assert hashed.startswith("$2b$")
        assert pwd_context.verify("my-password", hashed)

    def test_different_passwords_different_hashes(self):
        h1 = AuthService.hash_password("password-a")
        h2 = AuthService.hash_password("password-b")
        assert h1 != h2
