"""Merchant API endpoints — MERCH-004."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.modules.auth.models import User
from app.modules.merchant.schemas import (
    MerchantCategoryResponse,
    MerchantCreate,
    MerchantDetail,
    MerchantListItem,
    MerchantMatch,
    MerchantQuoteCreate,
    MerchantQuoteResponse,
    MerchantUpdate,
)
from app.modules.merchant.service import MerchantService

router = APIRouter(prefix="/api/v1/merchants", tags=["商户管理"])


@router.get("", response_model=PaginatedResponse[MerchantListItem])
async def list_merchants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: uuid.UUID | None = None,
    tier: str | None = None,
    search: str | None = None,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List merchants with optional category/tier filters."""
    service = MerchantService(db)
    return await service.get_merchants(
        params=PaginationParams(page=page, page_size=page_size),
        category_id=category_id,
        tier=tier,
        search=search,
    )


@router.get("/categories", response_model=list[MerchantCategoryResponse])
async def list_merchant_categories(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all merchant categories."""
    service = MerchantService(db)
    return await service.get_categories()


@router.get("/match/{product_id}", response_model=list[MerchantMatch])
async def match_merchants(
    product_id: uuid.UUID,
    limit: int = Query(3, ge=1, le=10),
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Find top N merchants with highest quote for a product."""
    service = MerchantService(db)
    return await service.match_merchants_for_product(product_id, limit=limit)


@router.get("/{merchant_id}", response_model=MerchantDetail)
async def get_merchant(
    merchant_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get merchant detail with decrypted sensitive fields."""
    service = MerchantService(db)
    return await service.get_merchant_detail(merchant_id)


@router.post("", response_model=MerchantListItem)
async def create_merchant(
    data: MerchantCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new merchant (sensitive fields encrypted automatically)."""
    service = MerchantService(db)
    merchant = await service.create_merchant(data)
    return MerchantListItem(
        id=merchant.id,
        name=merchant.name,
        contact_name=merchant.contact_name,
        tier=merchant.tier,
        total_orders=merchant.total_orders,
    )


@router.put("/{merchant_id}", response_model=MerchantListItem)
async def update_merchant(
    merchant_id: uuid.UUID,
    data: MerchantUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a merchant."""
    service = MerchantService(db)
    merchant = await service.update_merchant(merchant_id, data)
    return MerchantListItem(
        id=merchant.id,
        name=merchant.name,
        contact_name=merchant.contact_name,
        tier=merchant.tier,
        total_orders=merchant.total_orders,
    )


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a merchant."""
    service = MerchantService(db)
    await service.delete_merchant(merchant_id)
    return {"message": "Merchant deleted"}


@router.post("/{merchant_id}/quotes", response_model=MerchantQuoteResponse)
async def create_quote(
    merchant_id: uuid.UUID,
    data: MerchantQuoteCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a merchant's price quote for a product."""
    service = MerchantService(db)
    return await service.create_quote(merchant_id, data)
