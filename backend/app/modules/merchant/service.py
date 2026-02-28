"""Merchant service — MERCH-003/004/005."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.encryption import decrypt, encrypt
from app.core.exceptions import NotFoundException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.modules.merchant.models import Merchant, MerchantCategory, MerchantQuote
from app.modules.merchant.schemas import (
    MerchantCreate,
    MerchantDetail,
    MerchantListItem,
    MerchantMatch,
    MerchantQuoteCreate,
    MerchantQuoteResponse,
    MerchantUpdate,
)

# Sensitive fields that require AES-256 encryption/decryption
_ENCRYPTED_FIELDS = ("phone", "wechat", "address")


class MerchantService:
    """Service for merchant management with encrypted sensitive fields."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Merchants ---

    async def get_merchants(
        self,
        params: PaginationParams,
        category_id: uuid.UUID | None = None,
        tier: str | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[MerchantListItem]:
        """List merchants with optional filters and pagination."""
        query = select(Merchant).options(selectinload(Merchant.category))

        if category_id:
            query = query.where(Merchant.category_id == category_id)
        if tier:
            query = query.where(Merchant.tier == tier)
        if search:
            query = query.where(Merchant.name.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(Merchant.total_orders.desc())
        query = query.offset(params.offset).limit(params.page_size)
        result = await self.db.execute(query)
        merchants = result.scalars().all()

        items = [
            MerchantListItem(
                id=m.id,
                name=m.name,
                contact_name=m.contact_name,
                tier=m.tier,
                total_orders=m.total_orders,
                category=m.category,
            )
            for m in merchants
        ]

        return PaginatedResponse(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    async def get_merchant_detail(self, merchant_id: uuid.UUID) -> MerchantDetail:
        """Get merchant detail with decrypted sensitive fields and quote history."""
        result = await self.db.execute(
            select(Merchant)
            .options(
                selectinload(Merchant.category),
                selectinload(Merchant.quotes),
            )
            .where(Merchant.id == merchant_id)
        )
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("Merchant", str(merchant_id))

        return MerchantDetail(
            id=merchant.id,
            name=merchant.name,
            contact_name=merchant.contact_name,
            phone=decrypt(merchant.phone) if merchant.phone else None,
            wechat=decrypt(merchant.wechat) if merchant.wechat else None,
            address=decrypt(merchant.address) if merchant.address else None,
            tier=merchant.tier,
            total_orders=merchant.total_orders,
            category=merchant.category,
            quotes=merchant.quotes,
            created_at=merchant.created_at,
            updated_at=merchant.updated_at,
        )

    async def create_merchant(self, data: MerchantCreate) -> Merchant:
        """Create a new merchant with encrypted sensitive fields."""
        merchant_data = data.model_dump(exclude=set(_ENCRYPTED_FIELDS))

        merchant = Merchant(**merchant_data)
        # Encrypt sensitive fields before storage
        for field in _ENCRYPTED_FIELDS:
            value = getattr(data, field)
            if value:
                setattr(merchant, field, encrypt(value))

        self.db.add(merchant)
        await self.db.flush()
        return merchant

    async def update_merchant(
        self, merchant_id: uuid.UUID, data: MerchantUpdate
    ) -> Merchant:
        """Update merchant, re-encrypting sensitive fields as needed."""
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("Merchant", str(merchant_id))

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in _ENCRYPTED_FIELDS:
                setattr(merchant, field, encrypt(value) if value else None)
            else:
                setattr(merchant, field, value)

        return merchant

    async def delete_merchant(self, merchant_id: uuid.UUID) -> None:
        """Delete a merchant."""
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundException("Merchant", str(merchant_id))

        await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))
        merchant = (
            await self.db.execute(select(Merchant).where(Merchant.id == merchant_id))
        ).scalar_one()
        await self.db.delete(merchant)

    # --- Quotes ---

    async def create_quote(
        self, merchant_id: uuid.UUID, data: MerchantQuoteCreate
    ) -> MerchantQuote:
        """Record a merchant's price quote for a product."""
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundException("Merchant", str(merchant_id))

        quote = MerchantQuote(
            merchant_id=merchant_id,
            product_id=data.product_id,
            price=data.price,
            currency=data.currency,
        )
        self.db.add(quote)
        await self.db.flush()
        return quote

    # --- Matching ---

    async def match_merchants_for_product(
        self, product_id: uuid.UUID, limit: int = 3
    ) -> list[MerchantMatch]:
        """Find top N merchants with the highest quote for a given product."""
        result = await self.db.execute(
            select(MerchantQuote)
            .options(
                selectinload(MerchantQuote.merchant).selectinload(Merchant.category)
            )
            .where(MerchantQuote.product_id == product_id)
            .order_by(MerchantQuote.price.desc())
            .limit(limit)
        )
        quotes = result.scalars().all()

        matches = []
        for q in quotes:
            merchant_item = MerchantListItem(
                id=q.merchant.id,
                name=q.merchant.name,
                contact_name=q.merchant.contact_name,
                tier=q.merchant.tier,
                total_orders=q.merchant.total_orders,
                category=q.merchant.category,
            )
            quote_resp = MerchantQuoteResponse(
                id=q.id,
                merchant_id=q.merchant_id,
                product_id=q.product_id,
                price=q.price,
                currency=q.currency,
                quoted_at=q.quoted_at,
            )
            matches.append(MerchantMatch(merchant=merchant_item, quote=quote_resp))

        return matches

    # --- Categories ---

    async def get_categories(self) -> list[MerchantCategory]:
        """Get all merchant categories ordered by sort_order."""
        result = await self.db.execute(
            select(MerchantCategory).order_by(MerchantCategory.sort_order)
        )
        return list(result.scalars().all())
