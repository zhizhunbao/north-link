"""Price module service - PRICE-004/005."""

import csv
import io
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateException, NotFoundException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.modules.price.models import (
    Category,
    PriceRecord,
    Product,
    ProductFavorite,
)
from app.modules.price.schemas import (
    CSVImportResult,
    PriceRecordCreate,
    ProductCreate,
    ProductDetail,
    ProductListItem,
    ProductUpdate,
)


class PriceService:
    """Service for product and price management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Products ---

    async def get_products(
        self,
        params: PaginationParams,
        category_id: uuid.UUID | None = None,
        condition: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        user_id: uuid.UUID | None = None,
    ) -> PaginatedResponse[ProductListItem]:
        """List products with filters, sorting, and pagination."""
        query = select(Product).options(selectinload(Product.category))

        if category_id:
            query = query.where(Product.category_id == category_id)
        if condition:
            query = query.where(Product.condition == condition)
        if search:
            query = query.where(Product.name.ilike(f"%{search}%"))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Sort
        sort_column = getattr(Product, sort_by, Product.created_at)
        query = query.order_by(sort_column.desc())

        # Paginate
        query = query.offset(params.offset).limit(params.page_size)
        result = await self.db.execute(query)
        products = result.scalars().all()

        # Check favorites if user logged in
        favorite_ids: set[uuid.UUID] = set()
        if user_id:
            fav_result = await self.db.execute(
                select(ProductFavorite.product_id).where(
                    ProductFavorite.user_id == user_id
                )
            )
            favorite_ids = {row for row in fav_result.scalars().all()}

        items = [
            ProductListItem(
                id=p.id,
                name=p.name,
                sku=p.sku,
                brand=p.brand,
                condition=p.condition,
                category=p.category,
                is_favorited=p.id in favorite_ids,
            )
            for p in products
        ]

        return PaginatedResponse(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    async def get_product_detail(
        self, product_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> ProductDetail:
        """Get product detail with all price records."""
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.price_records),
            )
            .where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product", str(product_id))

        is_fav = False
        if user_id:
            fav = await self.db.execute(
                select(ProductFavorite).where(
                    ProductFavorite.user_id == user_id,
                    ProductFavorite.product_id == product_id,
                )
            )
            is_fav = fav.scalar_one_or_none() is not None

        return ProductDetail(
            id=product.id,
            name=product.name,
            sku=product.sku,
            brand=product.brand,
            condition=product.condition,
            attributes=product.attributes,
            category=product.category,
            price_records=product.price_records,
            is_favorited=is_fav,
            created_at=product.created_at,
        )

    async def create_product(self, data: ProductCreate) -> Product:
        """Create a new product."""
        existing = await self.db.execute(select(Product).where(Product.sku == data.sku))
        if existing.scalar_one_or_none():
            raise DuplicateException("Product", "sku")

        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.flush()
        return product

    async def update_product(
        self, product_id: uuid.UUID, data: ProductUpdate
    ) -> Product:
        """Update product fields."""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product", str(product_id))

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        return product

    async def delete_product(self, product_id: uuid.UUID) -> None:
        """Delete a product."""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        if not result.scalar_one_or_none():
            raise NotFoundException("Product", str(product_id))
        await self.db.execute(delete(Product).where(Product.id == product_id))

    # --- Price Records ---

    async def create_price_record(self, data: PriceRecordCreate) -> PriceRecord:
        """Manually add a price record."""
        result = await self.db.execute(
            select(Product).where(Product.id == data.product_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundException("Product", str(data.product_id))

        record = PriceRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def import_csv(self, file_content: str) -> CSVImportResult:
        """Import price records from CSV content.

        Expected columns: product_sku, source, region, price, currency, price_type
        """
        reader = csv.DictReader(io.StringIO(file_content))
        success = 0
        errors: list[str] = []
        total = 0

        for row_num, row in enumerate(reader, start=2):
            total += 1
            try:
                sku = row.get("product_sku", "").strip()
                if not sku:
                    errors.append(f"Row {row_num}: missing product_sku")
                    continue

                result = await self.db.execute(
                    select(Product).where(Product.sku == sku)
                )
                product = result.scalar_one_or_none()
                if not product:
                    errors.append(f"Row {row_num}: product SKU '{sku}' not found")
                    continue

                record = PriceRecord(
                    product_id=product.id,
                    source=row.get("source", "csv").strip(),
                    region=row.get("region", "CA").strip(),
                    price=float(row.get("price", 0)),
                    currency=row.get("currency", "CAD").strip(),
                    price_type=row.get("price_type", "retail").strip(),
                )
                self.db.add(record)
                success += 1
            except (ValueError, KeyError) as e:
                errors.append(f"Row {row_num}: {e}")

        return CSVImportResult(
            total_rows=total,
            success_count=success,
            error_count=len(errors),
            errors=errors[:50],
        )

    # --- Favorites ---

    async def toggle_favorite(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        """Toggle product favorite. Returns True if favorited, False if removed."""
        result = await self.db.execute(
            select(ProductFavorite).where(
                ProductFavorite.user_id == user_id,
                ProductFavorite.product_id == product_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            await self.db.delete(existing)
            return False

        fav = ProductFavorite(user_id=user_id, product_id=product_id)
        self.db.add(fav)
        return True

    async def get_favorites(
        self, user_id: uuid.UUID, params: PaginationParams
    ) -> PaginatedResponse[ProductListItem]:
        """Get user's favorite products."""
        query = (
            select(Product)
            .join(ProductFavorite, ProductFavorite.product_id == Product.id)
            .where(ProductFavorite.user_id == user_id)
            .options(selectinload(Product.category))
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.offset(params.offset).limit(params.page_size)
        result = await self.db.execute(query)
        products = result.scalars().all()

        items = [
            ProductListItem(
                id=p.id,
                name=p.name,
                sku=p.sku,
                brand=p.brand,
                condition=p.condition,
                category=p.category,
                is_favorited=True,
            )
            for p in products
        ]

        return PaginatedResponse(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    # --- Categories ---

    async def get_categories(self) -> list[Category]:
        """Get all product categories."""
        result = await self.db.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())
