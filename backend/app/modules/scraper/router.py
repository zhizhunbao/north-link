"""Scraper usage API router - BE-028."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.modules.auth.models import User
from app.modules.scraper.schemas import ScraperUsageResponse
from app.modules.scraper.service import ScraperService

router = APIRouter(prefix="/api/v1/scraper", tags=["采集统计"])


@router.get("/usage", response_model=ScraperUsageResponse)
async def get_usage(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scraper usage statistics for cost monitoring."""
    service = ScraperService(db)
    stats = await service.get_usage_stats()
    return ScraperUsageResponse(**stats)
