"""Notification management service - BE-026."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notification.models import Notification


class NotificationService:
    """Business logic for notification CRUD and status management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_notifications(
        self, user_id: uuid.UUID, unread_only: bool = False
    ) -> list[Notification]:
        """List notifications for a user."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        if unread_only:
            query = query.where(Notification.is_read.is_(False))
        result = await self.db.execute(query.limit(50))
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Count unread notifications."""
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        return result.scalar() or 0

    async def mark_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Mark a single notification as read."""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True)
        )
        return result.rowcount > 0

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """Mark all unread notifications as read. Returns count updated."""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        return result.rowcount

    async def create_notification(
        self,
        user_id: uuid.UUID,
        type_: str,
        title: str,
        content: str | None = None,
        metadata: dict | None = None,
    ) -> Notification:
        """Create a new notification (used by subscription checker)."""
        notification = Notification(
            user_id=user_id,
            type=type_,
            title=title,
            content=content,
            metadata_=metadata or {},
        )
        self.db.add(notification)
        await self.db.flush()
        return notification
