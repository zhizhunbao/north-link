"""Chat module Pydantic schemas - BE-001."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Chat Message ---


class ChatMessageCreate(BaseModel):
    """Send a new message in a chat session."""

    content: str = Field(..., min_length=1, max_length=5000)
    session_id: uuid.UUID | None = Field(
        None, description="Existing session ID; omit to create new session"
    )


class ChatMessageResponse(BaseModel):
    """Single chat message in response."""

    id: uuid.UUID
    role: str
    content: str
    metadata: dict = Field(default_factory=dict, alias="metadata_")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# --- Chat Session ---


class ChatSessionResponse(BaseModel):
    """Chat session summary for list view."""

    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetail(BaseModel):
    """Chat session with full message history."""

    id: uuid.UUID
    title: str | None
    messages: list[ChatMessageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- SSE Events ---


class SSEEvent(BaseModel):
    """Server-Sent Event payload for chat streaming."""

    type: str = Field(
        ...,
        description="Event type: thinking|tool_call|progress|result|content|done|error",
    )
    content: str | None = None
    platform: str | None = None
    status: str | None = None
    items: list[dict] | None = None
    metadata: dict | None = None
    message_id: uuid.UUID | None = None
