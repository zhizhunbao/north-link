"""Unit tests for profit calculator — pure functions, no I/O."""

import pytest

from app.modules.profit.calculator import (
    ProfitParams,
    ProfitResult,
    calculate_profit,
    _assess_risk,
)


class TestAssessRisk:
    """Test risk level classification."""

    def test_high_profit_returns_low_risk(self):
        assert _assess_risk(0.30) == "low"
        assert _assess_risk(0.15) == "low"

    def test_medium_profit_returns_medium_risk(self):
        assert _assess_risk(0.14) == "medium"
        assert _assess_risk(0.05) == "medium"

    def test_low_profit_returns_high_risk(self):
        assert _assess_risk(0.04) == "high"
        assert _assess_risk(0.0) == "high"
        assert _assess_risk(-0.10) == "high"

    def test_boundary_values(self):
        # Exact boundary at 15%
        assert _assess_risk(0.15) == "low"
        assert _assess_risk(0.1499) == "medium"
        # Exact boundary at 5%
        assert _assess_risk(0.05) == "medium"
        assert _assess_risk(0.0499) == "high"


class TestCalculateProfit:
    """Test profit calculation engine."""

    @pytest.fixture
    def default_params(self) -> ProfitParams:
        return ProfitParams(
            exchange_rate=5.0,
            tariff_rate=0.16,
            shipping_cost_cad=2.0,
            clearance_fee_cad=1.0,
            misc_fee_cad=0.5,
        )

    def test_basic_profitable_scenario(self, default_params):
        # Arrange: $100 CAD buy, ¥1000 CNY sell
        result = calculate_profit(
            ca_price_cad=100.0,
            cn_price_cny=1000.0,
            params=default_params,
        )

        # Assert
        assert isinstance(result, ProfitResult)
        assert result.ca_cost_cad == 100.0
        assert result.cn_selling_cny == 1000.0
        assert result.ca_cost_cny == 500.0  # 100 * 5.0
        assert result.shipping_cost_cny == 10.0  # 2.0 * 5.0
        assert result.tariff_cny == 160.0  # 1000 * 0.16
        assert result.profit_cny > 0
        assert result.risk_level in ("low", "medium", "high")

    def test_loss_scenario(self, default_params):
        # Arrange: expensive product, low sell price
        result = calculate_profit(
            ca_price_cad=200.0,
            cn_price_cny=500.0,
            params=default_params,
        )

        # Assert: costs exceed revenue
        assert result.profit_cny < 0
        assert result.profit_rate < 0
        assert result.risk_level == "high"

    def test_quantity_multiplier(self, default_params):
        single = calculate_profit(
            ca_price_cad=50.0,
            cn_price_cny=500.0,
            params=default_params,
            quantity=1,
        )
        double = calculate_profit(
            ca_price_cad=50.0,
            cn_price_cny=500.0,
            params=default_params,
            quantity=2,
        )

        # Costs and revenue should scale linearly
        assert double.ca_cost_cad == single.ca_cost_cad * 2
        assert double.cn_selling_cny == single.cn_selling_cny * 2

    def test_zero_revenue_no_division_error(self, default_params):
        result = calculate_profit(
            ca_price_cad=100.0,
            cn_price_cny=0.0,
            params=default_params,
        )
        assert result.profit_rate == 0.0
        assert result.cn_selling_cny == 0.0

    def test_zero_costs_max_profit(self):
        params = ProfitParams(
            exchange_rate=1.0,
            tariff_rate=0.0,
            shipping_cost_cad=0.0,
            clearance_fee_cad=0.0,
            misc_fee_cad=0.0,
        )
        result = calculate_profit(
            ca_price_cad=10.0,
            cn_price_cny=100.0,
            params=params,
        )
        # Only cost is purchase: 10 * 1.0 = 10 CNY, revenue = 100
        assert result.profit_cny == 90.0
        assert result.profit_rate == 0.9  # 90%
        assert result.risk_level == "low"

    def test_result_is_immutable(self, default_params):
        result = calculate_profit(
            ca_price_cad=100.0,
            cn_price_cny=1000.0,
            params=default_params,
        )
        with pytest.raises(AttributeError):
            result.profit_cny = 999.99  # type: ignore

    def test_rounding_precision(self, default_params):
        result = calculate_profit(
            ca_price_cad=33.33,
            cn_price_cny=333.33,
            params=default_params,
        )
        # All monetary fields should be rounded to 2 decimal places
        assert result.ca_cost_cny == round(result.ca_cost_cny, 2)
        assert result.shipping_cost_cny == round(result.shipping_cost_cny, 2)
        assert result.tariff_cny == round(result.tariff_cny, 2)
        assert result.profit_cny == round(result.profit_cny, 2)
        # Profit rate rounded to 4 decimal places
        assert result.profit_rate == round(result.profit_rate, 4)
