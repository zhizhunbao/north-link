"""Profit module Pydantic schemas — PROFIT-003."""

from pydantic import BaseModel, Field


class ProfitCalculateRequest(BaseModel):
    """Request to calculate profit for a product."""

    ca_price_cad: float = Field(..., gt=0, description="Canada purchase price in CAD")
    cn_price_cny: float = Field(..., gt=0, description="China selling price in CNY")
    quantity: int = Field(1, ge=1, description="Number of units")
    tariff_rate: float | None = Field(
        None, ge=0, le=1, description="Override tariff rate"
    )
    shipping_cost_cad: float = Field(
        0, ge=0, description="Shipping cost per unit in CAD"
    )
    clearance_fee_cad: float = Field(
        0, ge=0, description="Clearance fee per unit in CAD"
    )
    misc_fee_cad: float = Field(0, ge=0, description="Misc fee per unit in CAD")


class ProfitCalculateResponse(BaseModel):
    """Profit calculation result with full cost breakdown."""

    ca_cost_cad: float
    cn_selling_cny: float
    ca_cost_cny: float
    shipping_cost_cny: float
    tariff_cny: float
    clearance_fee_cny: float
    misc_fee_cny: float
    total_cost_cny: float
    profit_cny: float
    profit_rate: float
    risk_level: str
    exchange_rate_used: float


class ProfitBatchItem(BaseModel):
    """Single item in a batch profit calculation."""

    ca_price_cad: float = Field(..., gt=0)
    cn_price_cny: float = Field(..., gt=0)
    quantity: int = Field(1, ge=1)
    product_name: str | None = None


class ProfitBatchRequest(BaseModel):
    """Batch profit calculation request."""

    items: list[ProfitBatchItem] = Field(..., min_length=1, max_length=100)
    tariff_rate: float | None = Field(None, ge=0, le=1)
    shipping_cost_cad: float = Field(0, ge=0)
    clearance_fee_cad: float = Field(0, ge=0)
    misc_fee_cad: float = Field(0, ge=0)


class ProfitBatchItemResponse(BaseModel):
    """Result for a single item in the batch."""

    product_name: str | None
    profit_cny: float
    profit_rate: float
    risk_level: str


class ProfitBatchResponse(BaseModel):
    """Batch profit calculation response."""

    results: list[ProfitBatchItemResponse]
    total_profit_cny: float
    avg_profit_rate: float
    exchange_rate_used: float


class ProfitParamsResponse(BaseModel):
    """Current profit calculation parameters."""

    default_tariff_rate: float
    default_shipping_cost_cad: float
    default_clearance_fee_cad: float
    default_misc_fee_cad: float
    exchange_rate: float


class ProfitParamsUpdate(BaseModel):
    """Update profit calculation parameters (stored in settings)."""

    default_tariff_rate: float | None = Field(None, ge=0, le=1)
    default_shipping_cost_cad: float | None = Field(None, ge=0)
    default_clearance_fee_cad: float | None = Field(None, ge=0)
    default_misc_fee_cad: float | None = Field(None, ge=0)
