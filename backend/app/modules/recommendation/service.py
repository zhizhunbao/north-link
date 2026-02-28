"""Recommendation service — REC-001.

MVP scoring formula (from sprint-plan.md):
    score = profit_rate * 0.5 + (1 - risk_factor) * 0.3 + history_count * 0.2

Where:
    - profit_rate: 0-1 normalized profit margin
    - risk_factor: 0=low, 0.5=medium, 1=high
    - history_count: normalized merchant quote count (0-1)
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.merchant.models import MerchantQuote
from app.modules.price.models import Category, PriceRecord, Product
from app.modules.recommendation.schemas import (
    DailyRecommendationResponse,
    RecommendedProduct,
)

# Scoring weights
WEIGHT_PROFIT = 0.5
WEIGHT_RISK = 0.3
WEIGHT_HISTORY = 0.2

# Risk thresholds based on profit rate
RISK_THRESHOLDS = {
    "high": 0.40,  # profit_rate > 40% = risky (too good to be true)
    "medium": 0.15,  # 15-40% = moderate
    "low": 0.0,  # 0-15% = safe
}


def _classify_risk(profit_rate: float) -> tuple[str, float]:
    """Classify risk level and return (label, factor).

    High profit margins on cross-border goods often signal risk
    (fakes, customs issues, volatile pricing).
    """
    if profit_rate > RISK_THRESHOLDS["high"]:
        return "high", 1.0
    if profit_rate > RISK_THRESHOLDS["medium"]:
        return "medium", 0.5
    return "low", 0.0


def _score_product(row, max_quotes: int) -> RecommendedProduct | None:
    """Score a single product row; returns None if ineligible."""
    ca_price = float(row.ca_price)
    cn_price = float(row.cn_price)

    if ca_price <= 0:
        return None

    profit_rate = (cn_price - ca_price) / ca_price
    if profit_rate < 0:
        return None  # Negative-margin products are excluded

    clamped_rate = min(profit_rate, 1.0)
    risk_level, risk_factor = _classify_risk(profit_rate)
    norm_history = (row.quote_count or 0) / max_quotes

    score = (
        clamped_rate * WEIGHT_PROFIT
        + (1 - risk_factor) * WEIGHT_RISK
        + norm_history * WEIGHT_HISTORY
    )

    return RecommendedProduct(
        product_id=row.id,
        product_name=row.name,
        sku=row.sku,
        category_name=row.category_name,
        ca_price=ca_price,
        cn_price=cn_price,
        profit_rate=round(profit_rate, 4),
        risk_level=risk_level,
        score=round(score, 4),
        merchant_count=row.quote_count or 0,
        created_at=row.created_at,
    )


class RecommendationService:
    """Service for generating daily product recommendations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _fetch_product_data(self):
        """Fetch products with CA/CN prices and merchant quote counts."""
        ca_price_sub = (
            select(
                PriceRecord.product_id,
                func.max(PriceRecord.price).label("ca_price"),
            )
            .where(PriceRecord.region == "CA")
            .group_by(PriceRecord.product_id)
            .subquery()
        )

        cn_price_sub = (
            select(
                PriceRecord.product_id,
                func.max(PriceRecord.price).label("cn_price"),
            )
            .where(PriceRecord.region == "CN")
            .group_by(PriceRecord.product_id)
            .subquery()
        )

        quote_count_sub = (
            select(
                MerchantQuote.product_id,
                func.count(MerchantQuote.id).label("quote_count"),
            )
            .group_by(MerchantQuote.product_id)
            .subquery()
        )

        query = (
            select(
                Product.id,
                Product.name,
                Product.sku,
                Category.name.label("category_name"),
                ca_price_sub.c.ca_price,
                cn_price_sub.c.cn_price,
                quote_count_sub.c.quote_count,
                Product.created_at,
            )
            .join(Category, Product.category_id == Category.id)
            .outerjoin(ca_price_sub, Product.id == ca_price_sub.c.product_id)
            .outerjoin(cn_price_sub, Product.id == cn_price_sub.c.product_id)
            .outerjoin(quote_count_sub, Product.id == quote_count_sub.c.product_id)
            .where(
                ca_price_sub.c.ca_price.isnot(None),
                cn_price_sub.c.cn_price.isnot(None),
            )
        )

        result = await self.db.execute(query)
        return result.all()

    async def get_daily_recommendations(
        self, top_n: int = 5
    ) -> DailyRecommendationResponse:
        """Generate daily TOP-N product recommendations."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = await self._fetch_product_data()

        if not rows:
            return DailyRecommendationResponse(
                date=today, recommendations=[], total_evaluated=0
            )

        max_quotes = max((r.quote_count or 0) for r in rows) or 1
        scored = [
            p for row in rows if (p := _score_product(row, max_quotes)) is not None
        ]
        scored.sort(key=lambda p: p.score, reverse=True)

        return DailyRecommendationResponse(
            date=today,
            recommendations=scored[:top_n],
            total_evaluated=len(scored),
        )
