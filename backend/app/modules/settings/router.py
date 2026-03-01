"""Settings module API endpoints — SET-002."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.modules.auth.models import User
from app.modules.settings.schemas import (
    SettingBulkUpdate,
    SettingResponse,
    SettingUpdate,
)
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/settings", tags=["系统设置"])


@router.get("", response_model=list[SettingResponse])
async def list_settings(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all system settings."""
    service = SettingsService(db)
    return await service.list_settings()


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a setting by key."""
    service = SettingsService(db)
    return await service.get_setting(key)


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    data: SettingUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a setting value."""
    service = SettingsService(db)
    return await service.update_setting(key, data.value)


@router.put("/", response_model=list[SettingResponse])
async def bulk_update_settings(
    data: SettingBulkUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk update multiple settings."""
    service = SettingsService(db)
    return await service.bulk_update(data.settings)


@router.get("/export/data")
async def export_data(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all settings as JSON (data backup)."""
    service = SettingsService(db)
    data = await service.export_data()
    return JSONResponse(content=data)
