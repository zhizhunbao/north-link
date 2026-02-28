"""Recommendation module Pydantic schemas — REC-001."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class RecommendedProduct(BaseModel):
    """A single product recommendation with score breakdown."""

    product_id: uuid.UUID
    product_name: str
    sku: str
    category_name: str
    ca_price: float | None = None
    cn_price: float | None = None
    profit_rate: float
    risk_level: str  # low / medium / high
    score: float
    merchant_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyRecommendationResponse(BaseModel):
    """Daily TOP-N product recommendations."""

    date: str
    recommendations: list[RecommendedProduct]
    total_evaluated: int
