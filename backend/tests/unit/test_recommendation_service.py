"""Unit tests for the recommendation scoring functions."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.recommendation.service import (
    RecommendationService,
    _classify_risk,
    _score_product,
)


class TestClassifyRisk:
    """Tests for _classify_risk helper function."""

    def test_low_risk_zero(self):
        label, factor = _classify_risk(0.0)
        assert label == "low"
        assert factor == 0.0

    def test_low_risk_14_percent(self):
        label, factor = _classify_risk(0.14)
        assert label == "low"
        assert factor == 0.0

    def test_medium_risk_boundary(self):
        # RISK_THRESHOLDS["medium"] = 0.15
        # Condition: profit_rate > 0.15 → medium
        # 0.15 is NOT > 0.15, so it's still 'low'
        label, factor = _classify_risk(0.15)
        assert label == "low"
        assert factor == 0.0

    def test_medium_risk_just_above_boundary(self):
        label, factor = _classify_risk(0.16)
        assert label == "medium"
        assert factor == 0.5

    def test_medium_risk_30_percent(self):
        label, factor = _classify_risk(0.30)
        assert label == "medium"
        assert factor == 0.5

    def test_high_risk_boundary(self):
        # 0.40 is NOT > 0.40, so it's still 'medium'
        label, factor = _classify_risk(0.40)
        assert label == "medium"
        assert factor == 0.5

    def test_high_risk_above_threshold(self):
        label, factor = _classify_risk(0.41)
        assert label == "high"
        assert factor == 1.0

    def test_high_risk_very_high(self):
        label, factor = _classify_risk(0.99)
        assert label == "high"
        assert factor == 1.0


class TestScoreProduct:
    """Tests for _score_product function."""

    def _make_row(
        self,
        ca_price: float,
        cn_price: float,
        quote_count: int = 0,
        product_id: uuid.UUID | None = None,
    ):
        """Helper to create a mock product row."""
        return SimpleNamespace(
            id=product_id or uuid.uuid4(),
            name="Test Product",
            sku="TEST-001",
            category_name="Electronics",
            ca_price=ca_price,
            cn_price=cn_price,
            quote_count=quote_count,
            created_at=datetime.now(timezone.utc),
        )

    def test_returns_none_when_ca_price_zero(self):
        row = self._make_row(ca_price=0, cn_price=100.0)
        assert _score_product(row, max_quotes=1) is None

    def test_returns_none_when_ca_price_negative(self):
        row = self._make_row(ca_price=-1.0, cn_price=100.0)
        assert _score_product(row, max_quotes=1) is None

    def test_returns_none_when_profit_negative(self):
        # cn_price < ca_price → negative margin
        row = self._make_row(ca_price=100.0, cn_price=80.0)
        assert _score_product(row, max_quotes=1) is None

    def test_returns_product_when_valid(self):
        row = self._make_row(ca_price=100.0, cn_price=120.0)
        result = _score_product(row, max_quotes=1)
        assert result is not None
        assert result.profit_rate == pytest.approx(0.2, rel=1e-3)

    def test_score_components(self):
        # profit_rate=0.2, risk_level=medium(factor=0.5), quote_count=0, max_quotes=1
        # score = 0.2*0.5 + (1-0.5)*0.3 + 0*0.2 = 0.1 + 0.15 + 0 = 0.25
        row = self._make_row(ca_price=100.0, cn_price=120.0, quote_count=0)
        result = _score_product(row, max_quotes=1)
        assert result.score == pytest.approx(0.25, rel=1e-3)

    def test_history_bonus(self):
        # Same as above but with quotes: quote_count=1, max_quotes=1
        # score = 0.2*0.5 + 0.5*0.3 + 1.0*0.2 = 0.1 + 0.15 + 0.2 = 0.45
        row = self._make_row(ca_price=100.0, cn_price=120.0, quote_count=1)
        result = _score_product(row, max_quotes=1)
        assert result.score == pytest.approx(0.45, rel=1e-3)

    def test_profit_rate_clamped_at_1(self):
        # profit_rate = (500 - 100) / 100 = 4.0, but clamped to 1.0
        row = self._make_row(ca_price=100.0, cn_price=500.0, quote_count=0)
        result = _score_product(row, max_quotes=1)
        # clamped_rate=1.0, risk=high(1.0), norm_history=0
        # score = 1.0*0.5 + (1-1.0)*0.3 + 0 = 0.5
        assert result.score == pytest.approx(0.5, rel=1e-3)

    def test_product_fields_populated(self):
        pid = uuid.uuid4()
        row = self._make_row(ca_price=100.0, cn_price=115.0, product_id=pid)
        result = _score_product(row, max_quotes=1)
        assert result.product_id == pid
        assert result.product_name == "Test Product"
        assert result.sku == "TEST-001"
        assert result.category_name == "Electronics"
        assert result.ca_price == 100.0
        assert result.cn_price == 115.0


class TestRecommendationService:
    """Tests for RecommendationService.get_daily_recommendations."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_data(self):
        db = AsyncMock()
        db.execute.return_value = MagicMock(all=MagicMock(return_value=[]))
        service = RecommendationService(db)
        result = await service.get_daily_recommendations()
        assert result.recommendations == []
        assert result.total_evaluated == 0

    @pytest.mark.asyncio
    async def test_returns_top_n_recommendations(self):
        db = AsyncMock()
        rows = [
            SimpleNamespace(
                id=uuid.uuid4(),
                name=f"Product {i}",
                sku=f"SKU-{i:03d}",
                category_name="Electronics",
                ca_price=100.0,
                cn_price=120.0 + i,
                quote_count=i,
                created_at=datetime.now(timezone.utc),
            )
            for i in range(1, 6)
        ]
        db.execute.return_value = MagicMock(all=MagicMock(return_value=rows))
        service = RecommendationService(db)
        result = await service.get_daily_recommendations(top_n=3)
        assert len(result.recommendations) <= 3

    @pytest.mark.asyncio
    async def test_excludes_negative_margin_products(self):
        db = AsyncMock()
        rows = [
            SimpleNamespace(
                id=uuid.uuid4(),
                name="Unprofitable",
                sku="BAD-001",
                category_name="Test",
                ca_price=200.0,
                cn_price=100.0,  # negative margin
                quote_count=0,
                created_at=datetime.now(timezone.utc),
            )
        ]
        db.execute.return_value = MagicMock(all=MagicMock(return_value=rows))
        service = RecommendationService(db)
        result = await service.get_daily_recommendations()
        assert result.recommendations == []

    @pytest.mark.asyncio
    async def test_date_format(self):
        db = AsyncMock()
        db.execute.return_value = MagicMock(all=MagicMock(return_value=[]))
        service = RecommendationService(db)
        result = await service.get_daily_recommendations()
        # Should be YYYY-MM-DD format
        from datetime import date

        date.fromisoformat(result.date)  # should not raise

    @pytest.mark.asyncio
    async def test_recommendations_sorted_by_score_descending(self):
        db = AsyncMock()
        rows = [
            SimpleNamespace(
                id=uuid.uuid4(),
                name="Low Profit",
                sku="LP-001",
                category_name="Test",
                ca_price=100.0,
                cn_price=105.0,  # 5% margin, score ~low
                quote_count=0,
                created_at=datetime.now(timezone.utc),
            ),
            SimpleNamespace(
                id=uuid.uuid4(),
                name="Med Profit",
                sku="MP-001",
                category_name="Test",
                ca_price=100.0,
                cn_price=120.0,  # 20% margin, higher score
                quote_count=1,
                created_at=datetime.now(timezone.utc),
            ),
        ]
        db.execute.return_value = MagicMock(all=MagicMock(return_value=rows))
        service = RecommendationService(db)
        result = await service.get_daily_recommendations(top_n=5)
        scores = [r.score for r in result.recommendations]
        assert scores == sorted(scores, reverse=True)
