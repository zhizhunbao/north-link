"""Price module Pydantic schemas - PRICE-003."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Category ---


class CategoryResponse(BaseModel):
    """Category list/detail response."""

    id: uuid.UUID
    name: str
    default_tariff_rate: float
    icon: str | None = None

    model_config = {"from_attributes": True}


# --- Product ---


class ProductCreate(BaseModel):
    """Create a new product."""

    name: str = Field(..., max_length=200)
    sku: str = Field(..., max_length=100)
    category_id: uuid.UUID
    brand: str | None = Field(None, max_length=100)
    condition: str = Field("new", pattern=r"^(new|used|refurbished|clearance)$")
    attributes: dict = Field(default_factory=dict)


class ProductUpdate(BaseModel):
    """Update product fields (partial)."""

    name: str | None = Field(None, max_length=200)
    brand: str | None = Field(None, max_length=100)
    condition: str | None = Field(None, pattern=r"^(new|used|refurbished|clearance)$")
    attributes: dict | None = None


class ProductListItem(BaseModel):
    """Product in list view (compact)."""

    id: uuid.UUID
    name: str
    sku: str
    brand: str | None
    condition: str
    category: CategoryResponse | None = None
    lowest_ca_price: float | None = None
    highest_cn_price: float | None = None
    is_favorited: bool = False

    model_config = {"from_attributes": True}


class ProductDetail(BaseModel):
    """Product detail view with price records."""

    id: uuid.UUID
    name: str
    sku: str
    brand: str | None
    condition: str
    attributes: dict
    category: CategoryResponse | None = None
    price_records: list["PriceRecordResponse"] = []
    is_favorited: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# --- PriceRecord ---


class PriceRecordCreate(BaseModel):
    """Manually create a price record."""

    product_id: uuid.UUID
    source: str = Field("manual", max_length=50)
    region: str = Field(..., pattern=r"^(CA|CN)$")
    price: float = Field(..., gt=0)
    currency: str = Field(..., pattern=r"^(CAD|CNY)$")
    price_type: str = Field("retail", pattern=r"^(retail|wholesale|buyback)$")
    url: str | None = Field(None, max_length=500)


class PriceRecordResponse(BaseModel):
    """Price record response."""

    id: uuid.UUID
    source: str
    region: str
    price: float
    currency: str
    price_type: str
    url: str | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class CSVImportResult(BaseModel):
    """Result of CSV price import."""

    total_rows: int
    success_count: int
    error_count: int
    errors: list[str] = []
