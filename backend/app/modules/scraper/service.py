"""Scraper task management and usage tracking - BE-007 / BE-028."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.scraper.models import ScraperTask


class ScraperService:
    """Manages scraper task lifecycle and usage statistics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_task(
        self,
        trigger_type: str,
        trigger_id: uuid.UUID | None,
        platform: str,
        keywords: str,
    ) -> ScraperTask:
        """Create a new scraper task record."""
        task = ScraperTask(
            trigger_type=trigger_type,
            trigger_id=trigger_id,
            platform=platform,
            keywords=keywords,
            status="pending",
        )
        self.db.add(task)
        await self.db.flush()
        return task

    async def update_task_status(
        self,
        task_id: uuid.UUID,
        status: str,
        items_found: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Update task status after execution."""
        result = await self.db.execute(
            select(ScraperTask).where(ScraperTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            return

        task.status = status
        task.items_found = items_found
        task.error_message = error_message

        now = datetime.now(timezone.utc)
        if status == "running" and task.started_at is None:
            task.started_at = now
        if status in ("success", "failed"):
            task.completed_at = now

    async def get_today_count(self) -> int:
        """Count today's scraper tasks for usage limiting."""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = await self.db.execute(
            select(func.count(ScraperTask.id)).where(
                ScraperTask.created_at >= today_start
            )
        )
        return result.scalar() or 0

    async def get_usage_stats(self) -> dict:
        """Get usage statistics for dashboard display."""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        month_start = today_start.replace(day=1)

        # Today count
        today_result = await self.db.execute(
            select(func.count(ScraperTask.id)).where(
                ScraperTask.created_at >= today_start
            )
        )
        today_count = today_result.scalar() or 0

        # Month count
        month_result = await self.db.execute(
            select(func.count(ScraperTask.id)).where(
                ScraperTask.created_at >= month_start
            )
        )
        month_count = month_result.scalar() or 0

        # By platform
        platform_result = await self.db.execute(
            select(ScraperTask.platform, func.count(ScraperTask.id))
            .where(ScraperTask.created_at >= today_start)
            .group_by(ScraperTask.platform)
        )
        by_platform = {row[0]: row[1] for row in platform_result.all()}

        return {
            "today_count": today_count,
            "today_limit": 100,
            "month_count": month_count,
            "by_platform": by_platform,
        }
