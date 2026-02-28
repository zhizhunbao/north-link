"""Recommendation module API endpoints — REC-002."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.modules.auth.models import User
from app.modules.recommendation.schemas import DailyRecommendationResponse
from app.modules.recommendation.service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["每日推荐"])


@router.get("/daily", response_model=DailyRecommendationResponse)
async def get_daily_recommendations(
    top_n: int = Query(5, ge=1, le=20),
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily TOP-N product recommendations based on scoring algorithm."""
    service = RecommendationService(db)
    return await service.get_daily_recommendations(top_n=top_n)
