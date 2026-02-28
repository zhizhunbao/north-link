"""Order module Pydantic schemas — ORDER-002."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Order ---


class OrderCreate(BaseModel):
    """Create an order (purchase or sale)."""

    order_type: str = Field(..., pattern=r"^(purchase|sale)$")
    product_id: uuid.UUID
    merchant_id: uuid.UUID
    quantity: int = Field(1, ge=1)
    unit_cost: float = Field(..., gt=0)
    cost_currency: str = Field("CAD", pattern=r"^(CAD|CNY)$")
    selling_price: float | None = Field(None, ge=0)


class OrderUpdate(BaseModel):
    """Update order fields (partial)."""

    quantity: int | None = Field(None, ge=1)
    unit_cost: float | None = Field(None, gt=0)
    selling_price: float | None = Field(None, ge=0)
    status: str | None = Field(
        None,
        pattern=r"^(draft|confirmed|shipped|delivered|completed)$",
    )


class OrderResponse(BaseModel):
    """Order response with computed fields."""

    id: uuid.UUID
    order_type: str
    product_id: uuid.UUID
    merchant_id: uuid.UUID
    user_id: uuid.UUID
    quantity: int
    unit_cost: float
    cost_currency: str
    total_cost: float
    selling_price: float | None = None
    profit: float | None = None
    profit_rate: float | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Reports ---


class ProfitSummary(BaseModel):
    """Aggregated profit summary for a time period."""

    period: str
    total_revenue: float
    total_cost: float
    total_profit: float
    order_count: int
    avg_profit_rate: float


class ProductRanking(BaseModel):
    """Single product in a profit ranking."""

    product_id: uuid.UUID
    product_name: str
    total_quantity: int
    total_profit: float
    avg_profit_rate: float


class ReportResponse(BaseModel):
    """Full report with summary and rankings."""

    summaries: list[ProfitSummary]
    top_products: list[ProductRanking]
