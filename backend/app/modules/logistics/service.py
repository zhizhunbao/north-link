"""Logistics module service — LOGI-003/004."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ValidationException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.modules.logistics.models import (
    FreightAgent,
    FreightQuote,
    Shipment,
    TrackingEvent,
)
from app.modules.logistics.schemas import (
    FreightAgentCreate,
    FreightAgentUpdate,
    FreightQuoteCreate,
    LogisticsRecommendation,
    ShipmentCreate,
    ShipmentStatusUpdate,
    TrackingEventCreate,
)


class LogisticsService:
    """Service for freight agent, shipment, and tracking management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -- Freight Agent CRUD --

    async def list_agents(
        self,
        params: PaginationParams,
        rating: str | None = None,
    ) -> PaginatedResponse:
        """List freight agents with optional rating filter."""
        query = select(FreightAgent)
        count_query = select(func.count(FreightAgent.id))

        if rating:
            query = query.where(FreightAgent.rating == rating)
            count_query = count_query.where(FreightAgent.rating == rating)

        total = (await self.db.execute(count_query)).scalar() or 0
        query = (
            query.order_by(FreightAgent.rating, FreightAgent.unit_price)
            .offset(params.offset)
            .limit(params.page_size)
        )
        result = await self.db.execute(query)
        agents = list(result.scalars().all())

        return PaginatedResponse(
            items=agents,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_agent(self, agent_id: uuid.UUID) -> FreightAgent:
        """Get a freight agent by ID."""
        result = await self.db.execute(
            select(FreightAgent)
            .options(selectinload(FreightAgent.quotes))
            .where(FreightAgent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise NotFoundException("FreightAgent", str(agent_id))
        return agent

    async def create_agent(self, data: FreightAgentCreate) -> FreightAgent:
        """Create a new freight agent."""
        if data.est_days_min > data.est_days_max:
            raise ValidationException(
                "est_days_min must be <= est_days_max",
                code="INVALID_EST_DAYS",
            )
        agent = FreightAgent(**data.model_dump())
        self.db.add(agent)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def update_agent(
        self, agent_id: uuid.UUID, data: FreightAgentUpdate
    ) -> FreightAgent:
        """Update freight agent fields (partial)."""
        agent = await self.get_agent(agent_id)
        update_data = data.model_dump(exclude_unset=True)

        # Validate est_days consistency after update
        new_min = update_data.get("est_days_min", agent.est_days_min)
        new_max = update_data.get("est_days_max", agent.est_days_max)
        if new_min > new_max:
            raise ValidationException(
                "est_days_min must be <= est_days_max",
                code="INVALID_EST_DAYS",
            )

        for key, value in update_data.items():
            setattr(agent, key, value)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def delete_agent(self, agent_id: uuid.UUID) -> None:
        """Delete a freight agent (cascades to quotes)."""
        agent = await self.get_agent(agent_id)
        await self.db.delete(agent)
        await self.db.flush()

    # -- Freight Quote --

    async def create_quote(
        self, agent_id: uuid.UUID, data: FreightQuoteCreate
    ) -> FreightQuote:
        """Create a freight quote for a specific agent and category."""
        await self.get_agent(agent_id)  # Validate agent exists
        quote = FreightQuote(agent_id=agent_id, **data.model_dump())
        self.db.add(quote)
        await self.db.flush()
        await self.db.refresh(quote)
        return quote

    async def list_quotes(self, agent_id: uuid.UUID) -> list[FreightQuote]:
        """List all quotes for a freight agent."""
        result = await self.db.execute(
            select(FreightQuote)
            .where(FreightQuote.agent_id == agent_id)
            .order_by(FreightQuote.created_at.desc())
        )
        return list(result.scalars().all())

    # -- Shipment --

    async def create_shipment(self, data: ShipmentCreate) -> Shipment:
        """Create a shipment for an order."""
        shipment = Shipment(**data.model_dump())
        self.db.add(shipment)
        await self.db.flush()
        await self.db.refresh(shipment)
        return shipment

    async def get_shipment(self, shipment_id: uuid.UUID) -> Shipment:
        """Get shipment with agent and tracking events."""
        result = await self.db.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.freight_agent),
                selectinload(Shipment.tracking_events),
            )
            .where(Shipment.id == shipment_id)
        )
        shipment = result.scalar_one_or_none()
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        return shipment

    async def update_shipment_status(
        self, shipment_id: uuid.UUID, data: ShipmentStatusUpdate
    ) -> Shipment:
        """Update shipment status and tracking number."""
        shipment = await self.get_shipment(shipment_id)

        valid_transitions = {
            "pending": ["picked_up"],
            "picked_up": ["in_transit"],
            "in_transit": ["customs"],
            "customs": ["delivering"],
            "delivering": ["delivered"],
        }
        allowed = valid_transitions.get(shipment.status, [])
        if data.status not in allowed:
            raise ValidationException(
                f"Cannot transition from '{shipment.status}' to '{data.status}'",
                code="INVALID_STATUS_TRANSITION",
            )

        shipment.status = data.status
        if data.tracking_number is not None:
            shipment.tracking_number = data.tracking_number

        now = datetime.now(timezone.utc)
        if data.status == "picked_up":
            shipment.shipped_at = now
        elif data.status == "delivered":
            shipment.delivered_at = now

        await self.db.flush()
        await self.db.refresh(shipment)
        return shipment

    async def list_shipments(
        self,
        params: PaginationParams,
        status: str | None = None,
    ) -> PaginatedResponse:
        """List shipments with optional status filter."""
        query = select(Shipment).options(selectinload(Shipment.freight_agent))
        count_query = select(func.count(Shipment.id))

        if status:
            query = query.where(Shipment.status == status)
            count_query = count_query.where(Shipment.status == status)

        total = (await self.db.execute(count_query)).scalar() or 0
        query = (
            query.order_by(Shipment.created_at.desc())
            .offset(params.offset)
            .limit(params.page_size)
        )
        result = await self.db.execute(query)
        shipments = list(result.scalars().all())

        return PaginatedResponse(
            items=shipments,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    # -- Tracking Events --

    async def add_tracking_event(
        self, shipment_id: uuid.UUID, data: TrackingEventCreate
    ) -> TrackingEvent:
        """Add a tracking event to a shipment."""
        await self.get_shipment(shipment_id)  # Validate exists
        event = TrackingEvent(shipment_id=shipment_id, **data.model_dump())
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def list_tracking_events(self, shipment_id: uuid.UUID) -> list[TrackingEvent]:
        """List tracking events for a shipment (newest first)."""
        result = await self.db.execute(
            select(TrackingEvent)
            .where(TrackingEvent.shipment_id == shipment_id)
            .order_by(TrackingEvent.event_at.desc())
        )
        return list(result.scalars().all())

    # -- Logistics Recommendation (LOGI-004) --

    @staticmethod
    def _build_recommendation(
        quote: FreightQuote,
        agent: FreightAgent,
        weight_kg: float,
        reason: str,
    ) -> LogisticsRecommendation:
        """Build a LogisticsRecommendation from a quote/agent pair."""
        return LogisticsRecommendation(
            agent=agent,
            estimated_cost=float(quote.price) * weight_kg,
            est_days=f"{agent.est_days_min}-{agent.est_days_max}",
            recommendation_reason=reason,
        )

    @staticmethod
    def _pick_best(rows, seen: set, key_fn, filter_fn=None):
        """Pick the first unseen agent after sorting by key_fn."""
        sorted_rows = sorted(rows, key=key_fn)
        for quote, agent in sorted_rows:
            if agent.id in seen:
                continue
            if filter_fn and not filter_fn(agent):
                continue
            return quote, agent
        return None

    async def recommend_agents(
        self, category_id: uuid.UUID, weight_kg: float = 1.0
    ) -> list[LogisticsRecommendation]:
        """Recommend logistics options: cheapest, fastest, tax-included."""
        result = await self.db.execute(
            select(FreightQuote, FreightAgent)
            .join(FreightAgent, FreightQuote.agent_id == FreightAgent.id)
            .where(FreightQuote.category_id == category_id)
        )
        rows = result.all()
        if not rows:
            return []

        recommendations: list[LogisticsRecommendation] = []
        seen: set[uuid.UUID] = set()

        strategies = [
            (lambda r: float(r[0].price) * weight_kg, None, "最低运费"),
            (lambda r: r[1].est_days_min, None, "最快到达"),
            (lambda r: 0, lambda a: a.tax_included, "包税直邮"),
        ]
        for key_fn, filter_fn, reason in strategies:
            pick = self._pick_best(rows, seen, key_fn, filter_fn)
            if pick:
                quote, agent = pick
                recommendations.append(
                    self._build_recommendation(quote, agent, weight_kg, reason)
                )
                seen.add(agent.id)

        return recommendations
