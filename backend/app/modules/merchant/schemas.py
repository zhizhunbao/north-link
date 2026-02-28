"""Merchant module Pydantic schemas — MERCH-003."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- MerchantCategory ---


class MerchantCategoryResponse(BaseModel):
    """Merchant category response."""

    id: uuid.UUID
    name: str
    description: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


# --- Merchant ---


class MerchantCreate(BaseModel):
    """Create a new merchant. Sensitive fields in plaintext (encrypted at service layer)."""

    name: str = Field(..., max_length=100)
    category_id: uuid.UUID | None = None
    contact_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    wechat: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=200)
    tier: str = Field("bronze", pattern=r"^(gold|silver|bronze)$")


class MerchantUpdate(BaseModel):
    """Update merchant fields (partial)."""

    name: str | None = Field(None, max_length=100)
    category_id: uuid.UUID | None = None
    contact_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    wechat: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=200)
    tier: str | None = Field(None, pattern=r"^(gold|silver|bronze)$")


class MerchantListItem(BaseModel):
    """Merchant in list view."""

    id: uuid.UUID
    name: str
    contact_name: str | None = None
    tier: str
    total_orders: int
    category: MerchantCategoryResponse | None = None

    model_config = {"from_attributes": True}


class MerchantDetail(BaseModel):
    """Merchant detail with decrypted sensitive fields."""

    id: uuid.UUID
    name: str
    contact_name: str | None = None
    phone: str | None = None
    wechat: str | None = None
    address: str | None = None
    tier: str
    total_orders: int
    category: MerchantCategoryResponse | None = None
    quotes: list["MerchantQuoteResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- MerchantQuote ---


class MerchantQuoteCreate(BaseModel):
    """Create a merchant quote for a product."""

    product_id: uuid.UUID
    price: float = Field(..., gt=0)
    currency: str = Field("CNY", pattern=r"^(CNY|CAD)$")


class MerchantQuoteResponse(BaseModel):
    """Merchant quote response."""

    id: uuid.UUID
    merchant_id: uuid.UUID
    product_id: uuid.UUID
    price: float
    currency: str
    quoted_at: datetime

    model_config = {"from_attributes": True}


class MerchantMatch(BaseModel):
    """Merchant match result for a product — highest quote."""

    merchant: MerchantListItem
    quote: MerchantQuoteResponse
