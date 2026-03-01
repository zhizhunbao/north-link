"""Scraper module Pydantic schemas - BE-007."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ScraperTaskResponse(BaseModel):
    """Scraper task status response."""

    id: uuid.UUID
    trigger_type: str
    platform: str
    keywords: str
    status: str
    items_found: int
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScraperUsageResponse(BaseModel):
    """Daily/monthly scraper usage statistics."""

    today_count: int = 0
    today_limit: int = 100
    month_count: int = 0
    by_platform: dict[str, int] = Field(default_factory=dict)
