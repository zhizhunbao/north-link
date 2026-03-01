"""Integration tests for Logistics endpoints (Freight Agents)."""

import pytest
from httpx import AsyncClient

AGENTS_BASE = "/api/v1/logistics/agents"

SAMPLE_AGENT = {
    "name": "Speed Freight Ltd.",
    "unit_price": 8.5,
    "est_days_min": 3,
    "est_days_max": 7,
    "tax_included": True,
    "pickup_service": False,
    "rating": "A",
    "contact": "logistics@speed.com",
}


class TestFreightAgentRoutes:
    """Freight agent CRUD integration tests."""

    @pytest.mark.asyncio
    async def test_list_agents_unauthenticated(self, async_client: AsyncClient):
        resp = await async_client.get(AGENTS_BASE)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_agents_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.get(AGENTS_BASE, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_agent(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        resp = await async_client.post(
            AGENTS_BASE, json=SAMPLE_AGENT, headers=auth_headers
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == SAMPLE_AGENT["name"]
        assert data["rating"] == "A"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_agent_invalid_est_days(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """est_days_min > est_days_max should return 400."""
        resp = await async_client.post(
            AGENTS_BASE,
            json={**SAMPLE_AGENT, "est_days_min": 10, "est_days_max": 5},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_agent_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        import uuid
        resp = await async_client.get(
            f"{AGENTS_BASE}/{uuid.uuid4()}", headers=auth_headers
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_create_and_update_agent(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        create_resp = await async_client.post(
            AGENTS_BASE, json=SAMPLE_AGENT, headers=auth_headers
        )
        agent_id = create_resp.json()["id"]

        update_resp = await async_client.put(
            f"{AGENTS_BASE}/{agent_id}",
            json={"unit_price": 9.9, "rating": "B"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200
        assert float(update_resp.json()["unit_price"]) == pytest.approx(9.9)

    @pytest.mark.asyncio
    async def test_delete_agent(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        create_resp = await async_client.post(
            AGENTS_BASE, json=SAMPLE_AGENT, headers=auth_headers
        )
        agent_id = create_resp.json()["id"]

        del_resp = await async_client.delete(
            f"{AGENTS_BASE}/{agent_id}", headers=auth_headers
        )
        assert del_resp.status_code in (200, 204)

        get_resp = await async_client.get(
            f"{AGENTS_BASE}/{agent_id}", headers=auth_headers
        )
        assert get_resp.status_code == 404
