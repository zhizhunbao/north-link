"""Integration tests for Settings endpoints."""

import pytest
from httpx import AsyncClient

SETTINGS_BASE = "/api/v1/settings"


class TestSettingsRoutes:
    """Settings API endpoint integration tests."""

    @pytest.mark.asyncio
    async def test_list_settings_unauthenticated(self, async_client: AsyncClient):
        resp = await async_client.get(f"{SETTINGS_BASE}/")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_settings(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(f"{SETTINGS_BASE}/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_get_setting_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            f"{SETTINGS_BASE}/nonexistent_key_xyz", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_bulk_update_and_get(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Bulk update settings then retrieve one."""
        update_resp = await async_client.put(
            f"{SETTINGS_BASE}/",
            json={"settings": {"company_name": "NorthLink Test"}},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200

        get_resp = await async_client.get(
            f"{SETTINGS_BASE}/company_name", headers=auth_headers
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["value"] == "NorthLink Test"

    @pytest.mark.asyncio
    async def test_export_data(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(
            f"{SETTINGS_BASE}/export/data", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "exported_at" in data
        assert "settings" in data
