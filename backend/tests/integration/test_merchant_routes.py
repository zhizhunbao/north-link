"""Integration tests for Merchant endpoints.

Tests full CRUD flow against real DB (db-test container on port 5433).
"""

import pytest
from httpx import AsyncClient


MERCHANT_BASE = "/api/v1/merchants"

SAMPLE_MERCHANT = {
    "name": "Test Merchant Co.",
    "contact_name": "Alice",
    "phone": "13800138000",
    "tier": "gold",
}


class TestMerchantRoutes:
    """Merchant API endpoint integration tests."""

    @pytest.mark.asyncio
    async def test_list_merchants_unauthenticated(self, async_client: AsyncClient):
        """Listing merchants without auth returns 401."""
        resp = await async_client.get(f"{MERCHANT_BASE}/")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_merchants_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Fresh DB returns empty merchant list."""
        resp = await async_client.get(f"{MERCHANT_BASE}/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_merchant(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Create a merchant and verify response fields."""
        resp = await async_client.post(
            f"{MERCHANT_BASE}/", json=SAMPLE_MERCHANT, headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == SAMPLE_MERCHANT["name"]
        assert data["tier"] == SAMPLE_MERCHANT["tier"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_merchant_invalid_tier(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Invalid tier value returns 422."""
        resp = await async_client.post(
            f"{MERCHANT_BASE}/",
            json={**SAMPLE_MERCHANT, "tier": "INVALID"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_merchant_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Getting a non-existent merchant returns 404."""
        import uuid
        resp = await async_client.get(
            f"{MERCHANT_BASE}/{uuid.uuid4()}", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_create_and_get_merchant(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Create then fetch merchant detail — full round-trip."""
        create_resp = await async_client.post(
            f"{MERCHANT_BASE}/", json=SAMPLE_MERCHANT, headers=auth_headers
        )
        merchant_id = create_resp.json()["id"]

        get_resp = await async_client.get(
            f"{MERCHANT_BASE}/{merchant_id}", headers=auth_headers
        )
        assert get_resp.status_code == 200
        detail = get_resp.json()
        assert detail["id"] == merchant_id
        assert detail["name"] == SAMPLE_MERCHANT["name"]

    @pytest.mark.asyncio
    async def test_update_merchant(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Create, update name, verify change."""
        create_resp = await async_client.post(
            f"{MERCHANT_BASE}/", json=SAMPLE_MERCHANT, headers=auth_headers
        )
        merchant_id = create_resp.json()["id"]

        update_resp = await async_client.put(
            f"{MERCHANT_BASE}/{merchant_id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_merchant(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Create then delete a merchant — verify 404 afterwards."""
        create_resp = await async_client.post(
            f"{MERCHANT_BASE}/", json=SAMPLE_MERCHANT, headers=auth_headers
        )
        merchant_id = create_resp.json()["id"]

        del_resp = await async_client.delete(
            f"{MERCHANT_BASE}/{merchant_id}", headers=auth_headers
        )
        assert del_resp.status_code == 200

        get_resp = await async_client.get(
            f"{MERCHANT_BASE}/{merchant_id}", headers=auth_headers
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_categories(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Categories endpoint returns a list."""
        resp = await async_client.get(
            f"{MERCHANT_BASE}/categories", headers=auth_headers
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_list_merchants_after_create(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """After creating a merchant, list returns total=1."""
        await async_client.post(
            f"{MERCHANT_BASE}/", json=SAMPLE_MERCHANT, headers=auth_headers
        )
        resp = await async_client.get(f"{MERCHANT_BASE}/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
