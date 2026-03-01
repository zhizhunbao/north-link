"""Chat session management service - BE-002."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.chat.models import ChatMessage, ChatSession


class ChatService:
    """Business logic for chat session and message management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_sessions(self, user_id: uuid.UUID) -> list[ChatSession]:
        """List all chat sessions for a user, ordered by most recent."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_session_detail(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> ChatSession | None:
        """Get a session with all messages, scoped to user."""
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_session(
        self, user_id: uuid.UUID, title: str | None = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.flush()
        return session

    async def delete_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Delete a session (cascade deletes messages). Returns True if found."""
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if session is None:
            return False
        await self.db.delete(session)
        return True

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> ChatMessage:
        """Append a message to a session."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            metadata_=metadata or {},
        )
        self.db.add(message)
        # Touch session updated_at
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return message
