"""Notification module schemas and service - BE-025 / BE-026."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Notification item response."""

    id: uuid.UUID
    type: str
    title: str
    content: str | None = None
    metadata: dict = Field(default_factory=dict, alias="metadata_")
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class UnreadCountResponse(BaseModel):
    """Unread notification count."""

    count: int
