"""Price module API endpoints - PRICE-006."""

import uuid

from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.modules.auth.models import User
from app.modules.price.schemas import (
    CSVImportResult,
    CategoryResponse,
    PriceRecordCreate,
    PriceRecordResponse,
    ProductCreate,
    ProductDetail,
    ProductListItem,
    ProductUpdate,
)
from app.modules.price.service import PriceService

router = APIRouter(prefix="/api/v1/products", tags=["比价中心"])


@router.get("/", response_model=PaginatedResponse[ProductListItem])
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: uuid.UUID | None = None,
    condition: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List products with filters, pagination, and sort."""
    service = PriceService(db)
    return await service.get_products(
        params=PaginationParams(page=page, page_size=page_size),
        category_id=category_id,
        condition=condition,
        search=search,
        sort_by=sort_by,
        user_id=current_user.id,
    )


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all product categories."""
    service = PriceService(db)
    return await service.get_categories()


@router.get("/favorites", response_model=PaginatedResponse[ProductListItem])
async def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's favorite products."""
    service = PriceService(db)
    return await service.get_favorites(
        user_id=current_user.id,
        params=PaginationParams(page=page, page_size=page_size),
    )


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get product detail with all price records."""
    service = PriceService(db)
    return await service.get_product_detail(product_id, user_id=current_user.id)


@router.post("/", response_model=ProductListItem)
async def create_product(
    data: ProductCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""
    service = PriceService(db)
    return await service.create_product(data)


@router.put("/{product_id}", response_model=ProductListItem)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a product."""
    service = PriceService(db)
    return await service.update_product(product_id, data)


@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product."""
    service = PriceService(db)
    await service.delete_product(product_id)
    return {"message": "Product deleted"}


@router.post("/prices", response_model=PriceRecordResponse)
async def create_price_record(
    data: PriceRecordCreate,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually add a price record."""
    service = PriceService(db)
    return await service.create_price_record(data)


@router.post("/import", response_model=CSVImportResult)
async def import_csv(
    file: UploadFile,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import price records from CSV file."""
    content = (await file.read()).decode("utf-8")
    service = PriceService(db)
    return await service.import_csv(content)


@router.post("/{product_id}/favorite")
async def toggle_favorite(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle product favorite status."""
    service = PriceService(db)
    is_favorited = await service.toggle_favorite(current_user.id, product_id)
    return {"is_favorited": is_favorited}
