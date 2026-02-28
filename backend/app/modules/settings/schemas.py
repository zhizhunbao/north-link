"""Settings module Pydantic schemas — SET-001."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SettingResponse(BaseModel):
    """Setting response."""

    id: uuid.UUID
    key: str
    value: Any
    description: str | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    """Update a setting value."""

    value: Any = Field(..., description="JSON value for the setting")


class SettingBulkUpdate(BaseModel):
    """Bulk update multiple settings."""

    settings: dict[str, Any] = Field(
        ...,
        description="Map of setting key to new value",
    )
