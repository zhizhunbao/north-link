"""Subscription management service - BE-023."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.subscription.models import Subscription
from app.modules.subscription.schemas import SubscriptionCreate, SubscriptionUpdate

MAX_ACTIVE_SUBSCRIPTIONS = 20


class SubscriptionService:
    """Business logic for subscription CRUD and limit enforcement."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_subscriptions(
        self, user_id: uuid.UUID
    ) -> list[Subscription]:
        """List all subscriptions for a user."""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_subscription(
        self, user_id: uuid.UUID, data: SubscriptionCreate
    ) -> Subscription:
        """Create a subscription after checking the per-user limit."""
        active_count = await self._count_active(user_id)
        if active_count >= MAX_ACTIVE_SUBSCRIPTIONS:
            msg = f"Maximum {MAX_ACTIVE_SUBSCRIPTIONS} active subscriptions"
            raise ValueError(msg)

        sub = Subscription(
            user_id=user_id,
            product_id=data.product_id,
            platform=data.platform,
            target_type=data.target_type,
            target_value=data.target_value,
            threshold=data.threshold,
        )
        self.db.add(sub)
        await self.db.flush()
        return sub

    async def update_subscription(
        self,
        sub_id: uuid.UUID,
        user_id: uuid.UUID,
        data: SubscriptionUpdate,
    ) -> Subscription | None:
        """Update subscription fields. Returns None if not found."""
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.id == sub_id,
                Subscription.user_id == user_id,
            )
        )
        sub = result.scalar_one_or_none()
        if sub is None:
            return None

        if data.threshold is not None:
            sub.threshold = data.threshold
        if data.status is not None:
            sub.status = data.status
        return sub

    async def delete_subscription(
        self, sub_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Delete a subscription. Returns True if found and deleted."""
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.id == sub_id,
                Subscription.user_id == user_id,
            )
        )
        sub = result.scalar_one_or_none()
        if sub is None:
            return False
        await self.db.delete(sub)
        return True

    async def _count_active(self, user_id: uuid.UUID) -> int:
        """Count active subscriptions for limit enforcement."""
        result = await self.db.execute(
            select(func.count(Subscription.id)).where(
                Subscription.user_id == user_id,
                Subscription.status == "active",
            )
        )
        return result.scalar() or 0
