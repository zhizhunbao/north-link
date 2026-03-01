"""Subscription module Pydantic schemas - BE-022."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    """Create a new price tracking subscription."""

    platform: str = Field(..., max_length=30)
    target_type: str = Field(..., pattern=r"^(url|keyword)$")
    target_value: str = Field(..., min_length=1)
    threshold: float = Field(10.0, ge=1.0, le=100.0)
    product_id: uuid.UUID | None = None


class SubscriptionUpdate(BaseModel):
    """Update subscription fields."""

    threshold: float | None = Field(None, ge=1.0, le=100.0)
    status: str | None = Field(None, pattern=r"^(active|paused)$")


class SubscriptionResponse(BaseModel):
    """Subscription detail response."""

    id: uuid.UUID
    platform: str
    target_type: str
    target_value: str
    threshold: float
    status: str
    last_price: float | None = None
    last_checked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
