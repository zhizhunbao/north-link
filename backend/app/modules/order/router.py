"""Order module API endpoints — ORDER-003/005."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.modules.auth.models import User
from app.modules.order.schemas import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    ReportResponse,
)
from app.modules.order.service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["订单管理"])


# --- Order CRUD ---


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_type: str | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's orders with optional filters."""
    service = OrderService(db)
    return await service.list_orders(
        user_id=current_user.id,
        params=PaginationParams(page=page, page_size=page_size),
        order_type=order_type,
        status=status,
    )


@router.get("/reports", response_model=ReportResponse)
async def get_report(
    period: str = Query("monthly", pattern=r"^(daily|weekly|monthly)$"),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get profit report with summaries and product rankings."""
    service = OrderService(db)
    return await service.get_report(
        user_id=current_user.id,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get order detail."""
    service = OrderService(db)
    return await service.get_order(order_id)


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new order (profit auto-computed)."""
    service = OrderService(db)
    return await service.create_order(current_user.id, data)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: uuid.UUID,
    data: OrderUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update order fields (enforces status state machine)."""
    service = OrderService(db)
    return await service.update_order(order_id, data)


@router.delete("/{order_id}", status_code=204)
async def delete_order(
    order_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an order (only drafts can be deleted)."""
    service = OrderService(db)
    await service.delete_order(order_id)
