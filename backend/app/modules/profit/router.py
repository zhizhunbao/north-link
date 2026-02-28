"""Profit API endpoints — PROFIT-004."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.modules.auth.models import User
from app.modules.profit.schemas import (
    ProfitBatchRequest,
    ProfitBatchResponse,
    ProfitCalculateRequest,
    ProfitCalculateResponse,
    ProfitParamsResponse,
)
from app.modules.profit.service import ProfitService

router = APIRouter(prefix="/api/v1/profit", tags=["利润计算"])


@router.post("/calculate", response_model=ProfitCalculateResponse)
async def calculate_profit(
    data: ProfitCalculateRequest,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate profit for a single product with full cost breakdown."""
    service = ProfitService(db)
    return await service.calculate(data)


@router.post("/calculate/batch", response_model=ProfitBatchResponse)
async def calculate_profit_batch(
    data: ProfitBatchRequest,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate profit for multiple products at once."""
    service = ProfitService(db)
    return await service.calculate_batch(data)


@router.get("/params", response_model=ProfitParamsResponse)
async def get_profit_params(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current default profit calculation parameters."""
    service = ProfitService(db)
    return await service.get_params()
