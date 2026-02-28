"""Logistics module Pydantic schemas — LOGI-003."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- FreightAgent ---


class FreightAgentCreate(BaseModel):
    """Create a freight agent."""

    name: str = Field(..., max_length=100)
    unit_price: float = Field(..., gt=0)
    price_unit: str = Field("kg", pattern=r"^(kg|piece)$")
    est_days_min: int = Field(..., ge=1)
    est_days_max: int = Field(..., ge=1)
    tax_included: bool = False
    pickup_service: bool = False
    rating: str = Field("B", pattern=r"^[ABC]$")
    contact: str | None = Field(None, max_length=200)


class FreightAgentUpdate(BaseModel):
    """Update freight agent fields (partial)."""

    name: str | None = Field(None, max_length=100)
    unit_price: float | None = Field(None, gt=0)
    price_unit: str | None = Field(None, pattern=r"^(kg|piece)$")
    est_days_min: int | None = Field(None, ge=1)
    est_days_max: int | None = Field(None, ge=1)
    tax_included: bool | None = None
    pickup_service: bool | None = None
    rating: str | None = Field(None, pattern=r"^[ABC]$")
    contact: str | None = Field(None, max_length=200)


class FreightAgentResponse(BaseModel):
    """Freight agent response."""

    id: uuid.UUID
    name: str
    unit_price: float
    price_unit: str
    est_days_min: int
    est_days_max: int
    tax_included: bool
    pickup_service: bool
    rating: str
    contact: str | None = None

    model_config = {"from_attributes": True}


# --- FreightQuote ---


class FreightQuoteCreate(BaseModel):
    """Create a freight quote for a category."""

    category_id: uuid.UUID
    price: float = Field(..., gt=0)
    est_days: int = Field(..., ge=1)
    tax_included: bool = False
    valid_until: datetime | None = None


class FreightQuoteResponse(BaseModel):
    """Freight quote response."""

    id: uuid.UUID
    agent_id: uuid.UUID
    category_id: uuid.UUID
    price: float
    est_days: int
    tax_included: bool
    valid_until: datetime | None

    model_config = {"from_attributes": True}


# --- Shipment ---


class ShipmentCreate(BaseModel):
    """Create a shipment for an order."""

    order_id: uuid.UUID
    freight_agent_id: uuid.UUID
    tracking_number: str | None = Field(None, max_length=100)
    shipping_cost: float = Field(..., ge=0)
    tariff_cost: float = Field(0, ge=0)
    clearance_fee: float = Field(0, ge=0)


class ShipmentStatusUpdate(BaseModel):
    """Update shipment status."""

    status: str = Field(
        ..., pattern=r"^(pending|picked_up|in_transit|customs|delivering|delivered)$"
    )
    tracking_number: str | None = None


class ShipmentResponse(BaseModel):
    """Shipment response with agent info."""

    id: uuid.UUID
    order_id: uuid.UUID
    freight_agent: FreightAgentResponse | None = None
    tracking_number: str | None = None
    shipping_cost: float
    tariff_cost: float
    clearance_fee: float
    status: str
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- TrackingEvent ---


class TrackingEventCreate(BaseModel):
    """Create a tracking event."""

    status: str = Field(..., max_length=50)
    location: str | None = Field(None, max_length=200)
    description: str | None = None
    event_at: datetime


class TrackingEventResponse(BaseModel):
    """Tracking event response."""

    id: uuid.UUID
    status: str
    location: str | None = None
    description: str | None = None
    event_at: datetime

    model_config = {"from_attributes": True}


# --- Recommendation ---


class LogisticsRecommendation(BaseModel):
    """A recommended logistics option for shipping."""

    agent: FreightAgentResponse
    estimated_cost: float
    est_days: str
    recommendation_reason: str
