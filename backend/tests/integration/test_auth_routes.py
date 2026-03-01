"""Integration tests for Auth endpoints."""

import pytest
from httpx import AsyncClient


class TestAuthRoutes:
    """Auth API endpoint integration tests."""

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient):
        """Login with wrong credentials returns 401."""
        resp = await async_client.post("/api/v1/auth/login", json={
            "username": "nobody",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, async_client: AsyncClient):
        """Accessing /me without token returns 401."""
        resp = await async_client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, async_client: AsyncClient, auth_headers: dict):
        """Authenticated user can get their own info."""
        resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_change_password_wrong_old(self, async_client: AsyncClient, auth_headers: dict):
        """Changing password with wrong old password returns 400/401."""
        resp = await async_client.put("/api/v1/auth/password", json={
            "old_password": "WrongOldPassword!",
            "new_password": "NewPass5678!",
        }, headers=auth_headers)
        assert resp.status_code in (400, 401)

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        """Refreshing with an invalid token returns 401."""
        resp = await async_client.post("/api/v1/auth/refresh", json={
            "refresh_token": "this.is.not.a.valid.token",
        })
        assert resp.status_code == 401
