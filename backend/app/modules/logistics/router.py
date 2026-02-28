"""Logistics module API endpoints — LOGI-005."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.modules.auth.models import User
from app.modules.logistics.schemas import (
    FreightAgentCreate,
    FreightAgentResponse,
    FreightAgentUpdate,
    FreightQuoteCreate,
    FreightQuoteResponse,
    LogisticsRecommendation,
    ShipmentCreate,
    ShipmentResponse,
    ShipmentStatusUpdate,
    TrackingEventCreate,
    TrackingEventResponse,
)
from app.modules.logistics.service import LogisticsService

router = APIRouter(prefix="/api/v1/logistics", tags=["物流管理"])


# --- Freight Agents ---


@router.get("/agents", response_model=PaginatedResponse[FreightAgentResponse])
async def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    rating: str | None = None,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List freight agents with optional rating filter."""
    service = LogisticsService(db)
    return await service.list_agents(
        params=PaginationParams(page=page, page_size=page_size),
        rating=rating,
    )


@router.get("/agents/{agent_id}", response_model=FreightAgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get freight agent detail with quotes."""
    service = LogisticsService(db)
    return await service.get_agent(agent_id)


@router.post("/agents", response_model=FreightAgentResponse, status_code=201)
async def create_agent(
    data: FreightAgentCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new freight agent."""
    service = LogisticsService(db)
    return await service.create_agent(data)


@router.put("/agents/{agent_id}", response_model=FreightAgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    data: FreightAgentUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a freight agent."""
    service = LogisticsService(db)
    return await service.update_agent(agent_id, data)


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a freight agent."""
    service = LogisticsService(db)
    await service.delete_agent(agent_id)


# --- Freight Quotes ---


@router.get(
    "/agents/{agent_id}/quotes",
    response_model=list[FreightQuoteResponse],
)
async def list_quotes(
    agent_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List quotes for a freight agent."""
    service = LogisticsService(db)
    return await service.list_quotes(agent_id)


@router.post(
    "/agents/{agent_id}/quotes",
    response_model=FreightQuoteResponse,
    status_code=201,
)
async def create_quote(
    agent_id: uuid.UUID,
    data: FreightQuoteCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a freight quote for a specific agent."""
    service = LogisticsService(db)
    return await service.create_quote(agent_id, data)


# --- Shipments ---


@router.get("/shipments", response_model=PaginatedResponse[ShipmentResponse])
async def list_shipments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List shipments with optional status filter."""
    service = LogisticsService(db)
    return await service.list_shipments(
        params=PaginationParams(page=page, page_size=page_size),
        status=status,
    )


@router.post("/shipments", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    data: ShipmentCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new shipment for an order."""
    service = LogisticsService(db)
    return await service.create_shipment(data)


@router.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get shipment detail with tracking events."""
    service = LogisticsService(db)
    return await service.get_shipment(shipment_id)


@router.put(
    "/shipments/{shipment_id}/status",
    response_model=ShipmentResponse,
)
async def update_shipment_status(
    shipment_id: uuid.UUID,
    data: ShipmentStatusUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update shipment status (enforces state-machine transitions)."""
    service = LogisticsService(db)
    return await service.update_shipment_status(shipment_id, data)


# --- Tracking Events ---


@router.get(
    "/shipments/{shipment_id}/tracking",
    response_model=list[TrackingEventResponse],
)
async def list_tracking_events(
    shipment_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tracking events for a shipment (newest first)."""
    service = LogisticsService(db)
    return await service.list_tracking_events(shipment_id)


@router.post(
    "/shipments/{shipment_id}/tracking",
    response_model=TrackingEventResponse,
    status_code=201,
)
async def add_tracking_event(
    shipment_id: uuid.UUID,
    data: TrackingEventCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a tracking event to a shipment."""
    service = LogisticsService(db)
    return await service.add_tracking_event(shipment_id, data)


# --- Recommendation ---


@router.get(
    "/recommend/{category_id}",
    response_model=list[LogisticsRecommendation],
)
async def recommend_agents(
    category_id: uuid.UUID,
    weight_kg: float = Query(1.0, gt=0),
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get logistics recommendations for a product category."""
    service = LogisticsService(db)
    return await service.recommend_agents(category_id, weight_kg)
