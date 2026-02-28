"""Auth business logic - AUTH-003."""

from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.exceptions import AuthenticationException, NotFoundException
from app.modules.auth.models import User
from app.modules.auth.schemas import LoginRequest, PasswordChangeRequest, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, data: LoginRequest) -> TokenResponse:
        """Verify credentials and return JWT token pair."""
        result = await self.db.execute(
            select(User).where(User.username == data.username)
        )
        user = result.scalar_one_or_none()

        if user is None or not pwd_context.verify(data.password, user.password_hash):
            raise AuthenticationException("用户名或密码错误")

        if not user.is_active:
            raise AuthenticationException("账号已被禁用")

        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Generate a new access token from a valid refresh token."""
        user_id = verify_token(refresh_token, expected_type="refresh")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise AuthenticationException("无效的刷新令牌")

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def change_password(self, user_id: str, data: PasswordChangeRequest) -> None:
        """Change user password after verifying old password."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise NotFoundException("User", user_id)

        if not pwd_context.verify(data.old_password, user.password_hash):
            raise AuthenticationException("旧密码错误")

        user.password_hash = pwd_context.hash(data.new_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using bcrypt."""
        return pwd_context.hash(password)
