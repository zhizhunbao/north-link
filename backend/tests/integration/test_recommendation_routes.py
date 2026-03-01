"""Integration tests for Recommendation endpoint."""

import pytest
from httpx import AsyncClient

RECOMMENDATION_BASE = "/api/v1/recommendations"


class TestRecommendationRoutes:
    """Daily recommendation endpoint integration tests."""

    @pytest.mark.asyncio
    async def test_get_recommendations_unauthenticated(self, async_client: AsyncClient):
        resp = await async_client.get(f"{RECOMMENDATION_BASE}/daily")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_recommendations_empty_db(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """With no products, recommendations list is empty."""
        resp = await async_client.get(
            f"{RECOMMENDATION_BASE}/daily", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["recommendations"] == []
        assert data["total_evaluated"] == 0

    @pytest.mark.asyncio
    async def test_get_recommendations_returns_date(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Response always includes today's date."""
        from datetime import date
        resp = await async_client.get(
            f"{RECOMMENDATION_BASE}/daily", headers=auth_headers
        )
        assert resp.status_code == 200
        date.fromisoformat(resp.json()["date"])  # should not raise
