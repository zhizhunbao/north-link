"""Settings module service — SET-001/004."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.settings.models import Setting


class SettingsService:
    """Service for system settings management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_settings(self) -> list[Setting]:
        """List all system settings."""
        result = await self.db.execute(select(Setting).order_by(Setting.key))
        return list(result.scalars().all())

    async def get_setting(self, key: str) -> Setting:
        """Get a setting by key."""
        result = await self.db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if not setting:
            raise NotFoundException("Setting", key)
        return setting

    async def update_setting(self, key: str, value: Any) -> Setting:
        """Update a setting value by key."""
        setting = await self.get_setting(key)
        setting.value = value
        await self.db.flush()
        await self.db.refresh(setting)
        return setting

    async def bulk_update(self, updates: dict[str, Any]) -> list[Setting]:
        """Update multiple settings at once."""
        updated: list[Setting] = []
        for key, value in updates.items():
            try:
                setting = await self.get_setting(key)
                setting.value = value
                updated.append(setting)
            except NotFoundException:
                # Create new setting if it doesn't exist
                new_setting = Setting(key=key, value=value)
                self.db.add(new_setting)
                updated.append(new_setting)

        await self.db.flush()
        for s in updated:
            await self.db.refresh(s)
        return updated

    # -- Data Export (SET-004) --

    async def export_data(self) -> dict[str, Any]:
        """Export all settings as a JSON-serializable dictionary.

        This provides a basic data backup capability.
        Full database backup should use pg_dump in production.
        """
        settings = await self.list_settings()
        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "settings": [
                {
                    "key": s.key,
                    "value": s.value,
                    "description": s.description,
                }
                for s in settings
            ],
        }
