"""Profit calculator — pure functions, no I/O — PROFIT-002.

All monetary calculations for cross-border trade profit analysis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfitParams:
    """Parameters for profit calculation."""

    exchange_rate: float  # CAD → CNY
    tariff_rate: float  # e.g. 0.16 = 16%
    shipping_cost_cad: float  # shipping per unit in CAD
    clearance_fee_cad: float  # customs clearance fee per unit in CAD
    misc_fee_cad: float  # miscellaneous fees per unit in CAD


@dataclass(frozen=True)
class ProfitResult:
    """Computed profit breakdown."""

    ca_cost_cad: float  # Purchase cost in CAD
    cn_selling_cny: float  # Selling price in CNY
    ca_cost_cny: float  # Purchase cost converted to CNY
    shipping_cost_cny: float  # Shipping cost in CNY
    tariff_cny: float  # Tariff amount in CNY
    clearance_fee_cny: float  # Clearance fee in CNY
    misc_fee_cny: float  # Miscellaneous fee in CNY
    total_cost_cny: float  # Total cost in CNY
    profit_cny: float  # Net profit in CNY
    profit_rate: float  # Profit margin (0-1 scale)
    risk_level: str  # "low" / "medium" / "high"


def calculate_profit(
    ca_price_cad: float,
    cn_price_cny: float,
    params: ProfitParams,
    quantity: int = 1,
) -> ProfitResult:
    """Calculate profit for a single product (pure function, no side effects).

    Args:
        ca_price_cad: Canada purchase price per unit in CAD.
        cn_price_cny: China selling price per unit in CNY.
        params: Calculation parameters (exchange rate, tariff, shipping, etc.).
        quantity: Number of units (for total calculation).

    Returns:
        ProfitResult with full cost breakdown.
    """
    rate = params.exchange_rate

    # Convert CAD costs to CNY
    ca_cost_cny = ca_price_cad * rate * quantity
    shipping_cny = params.shipping_cost_cad * rate * quantity
    clearance_cny = params.clearance_fee_cad * rate * quantity
    misc_cny = params.misc_fee_cad * rate * quantity

    # Tariff is calculated on the CN selling price
    tariff_cny = cn_price_cny * params.tariff_rate * quantity

    # Total cost
    total_cost = ca_cost_cny + shipping_cny + tariff_cny + clearance_cny + misc_cny

    # Profit
    total_revenue = cn_price_cny * quantity
    profit = total_revenue - total_cost

    # Profit rate (avoid division by zero)
    profit_rate = profit / total_revenue if total_revenue > 0 else 0.0

    # Risk level based on profit rate
    risk_level = _assess_risk(profit_rate)

    return ProfitResult(
        ca_cost_cad=ca_price_cad * quantity,
        cn_selling_cny=total_revenue,
        ca_cost_cny=round(ca_cost_cny, 2),
        shipping_cost_cny=round(shipping_cny, 2),
        tariff_cny=round(tariff_cny, 2),
        clearance_fee_cny=round(clearance_cny, 2),
        misc_fee_cny=round(misc_cny, 2),
        total_cost_cny=round(total_cost, 2),
        profit_cny=round(profit, 2),
        profit_rate=round(profit_rate, 4),
        risk_level=risk_level,
    )


def _assess_risk(profit_rate: float) -> str:
    """Classify risk level based on profit margin.

    - >= 15%: low risk (green)
    - 5% ~ 15%: medium risk (yellow)
    - < 5%: high risk (red)
    """
    if profit_rate >= 0.15:
        return "low"
    if profit_rate >= 0.05:
        return "medium"
    return "high"
