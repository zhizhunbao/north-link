"""Subscription API router - BE-023."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.modules.auth.models import User
from app.modules.subscription.schemas import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from app.modules.subscription.service import SubscriptionService

router = APIRouter(prefix="/api/v1/subscriptions", tags=["订阅追踪"])


@router.get("", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all subscriptions for the current user."""
    service = SubscriptionService(db)
    return await service.get_subscriptions(current_user.id)


@router.post("", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new price tracking subscription."""
    service = SubscriptionService(db)
    try:
        return await service.create_subscription(current_user.id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{sub_id}", response_model=SubscriptionResponse)
async def update_subscription(
    sub_id: uuid.UUID,
    data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update subscription threshold or status."""
    service = SubscriptionService(db)
    sub = await service.update_subscription(sub_id, current_user.id, data)
    if sub is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@router.delete("/{sub_id}")
async def delete_subscription(
    sub_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a subscription."""
    service = SubscriptionService(db)
    deleted = await service.delete_subscription(sub_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription deleted"}
