"""Unit tests for LogisticsService."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.core.pagination import PaginationParams
from app.modules.logistics.schemas import (
    FreightAgentCreate,
    FreightAgentResponse,
    FreightAgentUpdate,
    FreightQuoteCreate,
    LogisticsRecommendation,
    ShipmentCreate,
    ShipmentStatusUpdate,
    TrackingEventCreate,
)
from app.modules.logistics.service import LogisticsService


def make_mock_agent(
    agent_id: uuid.UUID | None = None,
    rating: str = "A",
    est_days_min: int = 3,
    est_days_max: int = 7,
    tax_included: bool = False,
    unit_price: float = 10.0,
):
    agent = MagicMock()
    agent.id = agent_id or uuid.uuid4()
    agent.name = "Test Agent"
    agent.rating = rating
    agent.est_days_min = est_days_min
    agent.est_days_max = est_days_max
    agent.tax_included = tax_included
    agent.unit_price = unit_price
    agent.price_unit = "kg"
    agent.pickup_service = False
    agent.contact = None
    return agent


def make_mock_shipment(
    shipment_id: uuid.UUID | None = None,
    status: str = "pending",
):
    shipment = MagicMock()
    shipment.id = shipment_id or uuid.uuid4()
    shipment.status = status
    shipment.tracking_number = None
    shipment.shipped_at = None
    shipment.delivered_at = None
    return shipment


class TestLogisticsServiceAgentCRUD:
    """Tests for freight agent CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = LogisticsService(mock_db)
        with pytest.raises(NotFoundException):
            await service.get_agent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_agent_success(self, mock_db):
        agent = make_mock_agent()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=agent)
        )
        service = LogisticsService(mock_db)
        result = await service.get_agent(agent.id)
        assert result == agent

    @pytest.mark.asyncio
    async def test_create_agent_validates_est_days(self, mock_db):
        service = LogisticsService(mock_db)
        data = FreightAgentCreate(
            name="Test Agent",
            contact="John",
            rating="A",
            unit_price=10.0,
            est_days_min=10,
            est_days_max=5,  # max < min
            tax_included=False,
        )
        with pytest.raises(ValidationException):
            await service.create_agent(data)

    @pytest.mark.asyncio
    async def test_create_agent_success(self, mock_db):
        agent = make_mock_agent()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        service = LogisticsService(mock_db)
        data = FreightAgentCreate(
            name="Fast Freight",
            contact="Alice",
            rating="A",
            unit_price=8.5,
            est_days_min=3,
            est_days_max=7,
            tax_included=True,
        )
        with patch(
            "app.modules.logistics.service.FreightAgent", return_value=agent
        ):
            result = await service.create_agent(data)
        mock_db.add.assert_called_once_with(agent)
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_agent_success(self, mock_db):
        agent = make_mock_agent()
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=agent)
        )
        mock_db.delete = AsyncMock()
        service = LogisticsService(mock_db)
        await service.delete_agent(agent.id)
        mock_db.delete.assert_called_once_with(agent)

    @pytest.mark.asyncio
    async def test_update_agent_validates_est_days(self, mock_db):
        agent = make_mock_agent(est_days_min=3, est_days_max=7)
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=agent)
        )
        service = LogisticsService(mock_db)
        data = FreightAgentUpdate(est_days_min=10, est_days_max=5)
        with pytest.raises(ValidationException):
            await service.update_agent(agent.id, data)

    @pytest.mark.asyncio
    async def test_update_agent_success(self, mock_db):
        agent = make_mock_agent(est_days_min=3, est_days_max=7)
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=agent)
        )
        service = LogisticsService(mock_db)
        data = FreightAgentUpdate(est_days_min=2)
        result = await service.update_agent(agent.id, data)
        assert result == agent


class TestLogisticsServiceShipment:
    """Tests for shipment operations."""

    @pytest.mark.asyncio
    async def test_create_shipment(self, mock_db):
        shipment = make_mock_shipment()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        service = LogisticsService(mock_db)
        agent_id = uuid.uuid4()
        order_id = uuid.uuid4()
        data = ShipmentCreate(
            order_id=order_id,
            freight_agent_id=agent_id,
            shipping_cost=50.0,
        )
        with patch(
            "app.modules.logistics.service.Shipment", return_value=shipment
        ):
            result = await service.create_shipment(data)
        mock_db.add.assert_called_once_with(shipment)

    @pytest.mark.asyncio
    async def test_get_shipment_not_found(self, mock_db):
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )
        service = LogisticsService(mock_db)
        with pytest.raises(NotFoundException):
            await service.get_shipment(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_update_shipment_status_valid_transition(self, mock_db):
        shipment = make_mock_shipment(status="pending")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=shipment)
        )
        service = LogisticsService(mock_db)
        data = ShipmentStatusUpdate(status="picked_up")
        result = await service.update_shipment_status(shipment.id, data)
        assert shipment.status == "picked_up"
        assert shipment.shipped_at is not None

    @pytest.mark.asyncio
    async def test_update_shipment_status_invalid_transition(self, mock_db):
        shipment = make_mock_shipment(status="pending")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=shipment)
        )
        service = LogisticsService(mock_db)
        data = ShipmentStatusUpdate(status="delivered")  # can't jump from pending
        with pytest.raises(ValidationException):
            await service.update_shipment_status(shipment.id, data)

    @pytest.mark.asyncio
    async def test_update_shipment_delivered_sets_delivered_at(self, mock_db):
        shipment = make_mock_shipment(status="delivering")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=shipment)
        )
        service = LogisticsService(mock_db)
        data = ShipmentStatusUpdate(status="delivered")
        await service.update_shipment_status(shipment.id, data)
        assert shipment.delivered_at is not None

    @pytest.mark.asyncio
    async def test_update_shipment_tracking_number(self, mock_db):
        shipment = make_mock_shipment(status="pending")
        mock_db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=shipment)
        )
        service = LogisticsService(mock_db)
        data = ShipmentStatusUpdate(status="picked_up", tracking_number="TRK-001")
        await service.update_shipment_status(shipment.id, data)
        assert shipment.tracking_number == "TRK-001"


class TestLogisticsServiceRecommendation:
    """Tests for recommend_agents static methods and main method."""

    def test_build_recommendation(self):
        quote = MagicMock()
        quote.price = 5.0
        # Use make_mock_agent which has all required FreightAgentResponse attributes
        agent_orm = make_mock_agent(est_days_min=3, est_days_max=7)
        result = LogisticsService._build_recommendation(
            quote=quote, agent=agent_orm, weight_kg=2.0, reason="最低运费"
        )
        assert result.estimated_cost == pytest.approx(10.0)
        assert result.est_days == "3-7"
        assert result.recommendation_reason == "最低运费"

    def test_pick_best_returns_first_unseen(self):
        agent1 = MagicMock()
        agent1.id = uuid.uuid4()
        agent2 = MagicMock()
        agent2.id = uuid.uuid4()
        quote1 = MagicMock()
        quote1.price = 10
        quote2 = MagicMock()
        quote2.price = 5
        rows = [(quote1, agent1), (quote2, agent2)]
        seen = set()
        result = LogisticsService._pick_best(rows, seen, key_fn=lambda r: float(r[0].price))
        assert result is not None
        _, agent = result
        assert agent == agent2  # agent2 has lower price

    def test_pick_best_skips_seen_agents(self):
        agent = MagicMock()
        agent.id = uuid.uuid4()
        quote = MagicMock()
        quote.price = 5
        rows = [(quote, agent)]
        seen = {agent.id}
        result = LogisticsService._pick_best(rows, seen, key_fn=lambda r: float(r[0].price))
        assert result is None

    def test_pick_best_applies_filter(self):
        agent1 = MagicMock()
        agent1.id = uuid.uuid4()
        agent1.tax_included = False
        agent2 = MagicMock()
        agent2.id = uuid.uuid4()
        agent2.tax_included = True
        quote = MagicMock()
        quote.price = 5
        rows = [(quote, agent1), (quote, agent2)]
        seen = set()
        result = LogisticsService._pick_best(
            rows, seen, key_fn=lambda r: 0, filter_fn=lambda a: a.tax_included
        )
        assert result is not None
        _, agent = result
        assert agent == agent2

    @pytest.mark.asyncio
    async def test_recommend_agents_empty_returns_empty_list(self, mock_db):
        mock_db.execute.return_value = MagicMock(all=MagicMock(return_value=[]))
        service = LogisticsService(mock_db)
        result = await service.recommend_agents(uuid.uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_recommend_agents_returns_up_to_3(self, mock_db):
        category_id = uuid.uuid4()
        agent = make_mock_agent(tax_included=True, est_days_min=2, est_days_max=5)
        quote = MagicMock()
        quote.price = 5.0
        quote.agent_id = agent.id

        mock_db.execute.return_value = MagicMock(
            all=MagicMock(return_value=[(quote, agent)])
        )
        service = LogisticsService(mock_db)
        result = await service.recommend_agents(category_id, weight_kg=1.0)
        assert isinstance(result, list)
        assert len(result) >= 1
