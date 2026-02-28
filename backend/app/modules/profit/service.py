"""Profit service — PROFIT-003."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.profit.calculator import ProfitParams, ProfitResult, calculate_profit
from app.modules.profit.exchange_rate import get_exchange_rate
from app.modules.profit.schemas import (
    ProfitBatchRequest,
    ProfitBatchResponse,
    ProfitBatchItemResponse,
    ProfitCalculateRequest,
    ProfitCalculateResponse,
    ProfitParamsResponse,
)

# Default profit calculation parameters (MVP hardcoded; V1.5 from Settings table)
DEFAULT_TARIFF_RATE = 0.16
DEFAULT_SHIPPING_CAD = 15.0
DEFAULT_CLEARANCE_CAD = 10.0
DEFAULT_MISC_CAD = 5.0


class ProfitService:
    """Profit calculation service — orchestrates calculator + exchange rate."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(self, data: ProfitCalculateRequest) -> ProfitCalculateResponse:
        """Calculate profit for a single product."""
        rate = await get_exchange_rate(self.db)

        params = ProfitParams(
            exchange_rate=rate,
            tariff_rate=data.tariff_rate
            if data.tariff_rate is not None
            else DEFAULT_TARIFF_RATE,
            shipping_cost_cad=data.shipping_cost_cad or DEFAULT_SHIPPING_CAD,
            clearance_fee_cad=data.clearance_fee_cad or DEFAULT_CLEARANCE_CAD,
            misc_fee_cad=data.misc_fee_cad or DEFAULT_MISC_CAD,
        )

        result = calculate_profit(
            ca_price_cad=data.ca_price_cad,
            cn_price_cny=data.cn_price_cny,
            params=params,
            quantity=data.quantity,
        )

        return ProfitCalculateResponse(
            **_result_to_dict(result),
            exchange_rate_used=rate,
        )

    async def calculate_batch(self, data: ProfitBatchRequest) -> ProfitBatchResponse:
        """Calculate profit for multiple products at once."""
        rate = await get_exchange_rate(self.db)

        params = ProfitParams(
            exchange_rate=rate,
            tariff_rate=data.tariff_rate
            if data.tariff_rate is not None
            else DEFAULT_TARIFF_RATE,
            shipping_cost_cad=data.shipping_cost_cad or DEFAULT_SHIPPING_CAD,
            clearance_fee_cad=data.clearance_fee_cad or DEFAULT_CLEARANCE_CAD,
            misc_fee_cad=data.misc_fee_cad or DEFAULT_MISC_CAD,
        )

        results: list[ProfitBatchItemResponse] = []
        total_profit = 0.0
        total_rates: list[float] = []

        for item in data.items:
            result = calculate_profit(
                ca_price_cad=item.ca_price_cad,
                cn_price_cny=item.cn_price_cny,
                params=params,
                quantity=item.quantity,
            )
            results.append(
                ProfitBatchItemResponse(
                    product_name=item.product_name,
                    profit_cny=result.profit_cny,
                    profit_rate=result.profit_rate,
                    risk_level=result.risk_level,
                )
            )
            total_profit += result.profit_cny
            total_rates.append(result.profit_rate)

        avg_rate = sum(total_rates) / len(total_rates) if total_rates else 0.0

        return ProfitBatchResponse(
            results=results,
            total_profit_cny=round(total_profit, 2),
            avg_profit_rate=round(avg_rate, 4),
            exchange_rate_used=rate,
        )

    async def get_params(self) -> ProfitParamsResponse:
        """Get current default profit calculation parameters."""
        rate = await get_exchange_rate(self.db)
        return ProfitParamsResponse(
            default_tariff_rate=DEFAULT_TARIFF_RATE,
            default_shipping_cost_cad=DEFAULT_SHIPPING_CAD,
            default_clearance_fee_cad=DEFAULT_CLEARANCE_CAD,
            default_misc_fee_cad=DEFAULT_MISC_CAD,
            exchange_rate=rate,
        )


def _result_to_dict(result: ProfitResult) -> dict:
    """Convert ProfitResult dataclass to dict for Pydantic serialization."""
    return {
        "ca_cost_cad": result.ca_cost_cad,
        "cn_selling_cny": result.cn_selling_cny,
        "ca_cost_cny": result.ca_cost_cny,
        "shipping_cost_cny": result.shipping_cost_cny,
        "tariff_cny": result.tariff_cny,
        "clearance_fee_cny": result.clearance_fee_cny,
        "misc_fee_cny": result.misc_fee_cny,
        "total_cost_cny": result.total_cost_cny,
        "profit_cny": result.profit_cny,
        "profit_rate": result.profit_rate,
        "risk_level": result.risk_level,
    }
