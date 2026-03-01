"""Integration tests for Price (Product) endpoints."""
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.price.models import Category

PRODUCT_BASE = "/api/v1/products"


@pytest_asyncio.fixture(scope="function")
async def sample_category(db_session: AsyncSession) -> Category:
    cat = Category(name="Electronics", default_tariff_rate=0.16, icon="phone")
    db_session.add(cat)
    await db_session.flush()
    return cat


def _product_payload(category_id: uuid.UUID) -> dict:
    return {
        "name": "iPhone 15 Pro",
        "sku": "APPLE-IP15P-256",
        "category_id": str(category_id),
        "brand": "Apple",
        "condition": "new",
    }


class TestProductRoutes:

    @pytest.mark.asyncio
    async def test_list_products_unauthenticated(self, async_client: AsyncClient):
        resp = await async_client.get(f"{PRODUCT_BASE}/")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_products_empty(self, async_client, auth_headers):
        resp = await async_client.get(f"{PRODUCT_BASE}/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_create_product(self, async_client, auth_headers, sample_category):
        payload = _product_payload(sample_category.id)
        resp = await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["sku"] == payload["sku"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(self, async_client, auth_headers, sample_category):
        payload = _product_payload(sample_category.id)
        await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        resp = await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, async_client, auth_headers):
        resp = await async_client.get(f"{PRODUCT_BASE}/{uuid.uuid4()}", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_create_and_get_product(self, async_client, auth_headers, sample_category):
        payload = _product_payload(sample_category.id)
        create_resp = await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        product_id = create_resp.json()["id"]
        resp = await async_client.get(f"{PRODUCT_BASE}/{product_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["sku"] == payload["sku"]

    @pytest.mark.asyncio
    async def test_update_product(self, async_client, auth_headers, sample_category):
        payload = _product_payload(sample_category.id)
        create_resp = await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        product_id = create_resp.json()["id"]
        resp = await async_client.put(f"{PRODUCT_BASE}/{product_id}", json={"name": "iPhone 15 Pro Max", "condition": "refurbished"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "iPhone 15 Pro Max"

    @pytest.mark.asyncio
    async def test_delete_product(self, async_client, auth_headers, sample_category):
        payload = _product_payload(sample_category.id)
        create_resp = await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        product_id = create_resp.json()["id"]
        del_resp = await async_client.delete(f"{PRODUCT_BASE}/{product_id}", headers=auth_headers)
        assert del_resp.status_code in (200, 204)
        get_resp = await async_client.get(f"{PRODUCT_BASE}/{product_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_favorite(self, async_client, auth_headers, sample_category):
        payload = _product_payload(sample_category.id)
        create_resp = await async_client.post(f"{PRODUCT_BASE}/", json=payload, headers=auth_headers)
        product_id = create_resp.json()["id"]
        resp = await async_client.post(f"{PRODUCT_BASE}/{product_id}/favorite", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["is_favorited"] is True
        resp2 = await async_client.post(f"{PRODUCT_BASE}/{product_id}/favorite", headers=auth_headers)
        assert resp2.json()["is_favorited"] is False