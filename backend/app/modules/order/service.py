"""Order module service — ORDER-002/004."""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.core.pagination import PaginatedResponse, PaginationParams
from app.modules.order.models import Order
from app.modules.order.schemas import (
    OrderCreate,
    OrderUpdate,
    ProductRanking,
    ProfitSummary,
    ReportResponse,
)
from app.modules.price.models import Product


# Valid status transitions for the order state machine.
ORDER_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["confirmed"],
    "confirmed": ["shipped"],
    "shipped": ["delivered"],
    "delivered": ["completed"],
}


class OrderService:
    """Service for order management and reporting."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -- Order CRUD --

    async def list_orders(
        self,
        user_id: uuid.UUID,
        params: PaginationParams,
        order_type: str | None = None,
        status: str | None = None,
    ) -> PaginatedResponse:
        """List orders for a user with optional filters."""
        query = select(Order).where(Order.user_id == user_id)
        count_query = select(func.count(Order.id)).where(Order.user_id == user_id)

        if order_type:
            query = query.where(Order.order_type == order_type)
            count_query = count_query.where(Order.order_type == order_type)
        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)

        total = (await self.db.execute(count_query)).scalar() or 0
        query = (
            query.order_by(Order.created_at.desc())
            .offset(params.offset)
            .limit(params.page_size)
        )
        result = await self.db.execute(query)
        orders = list(result.scalars().all())

        return PaginatedResponse(
            items=orders,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_order(self, order_id: uuid.UUID) -> Order:
        """Get an order by ID."""
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundException("Order", str(order_id))
        return order

    async def create_order(self, user_id: uuid.UUID, data: OrderCreate) -> Order:
        """Create a new order, computing total_cost and profit."""
        total_cost = data.unit_cost * data.quantity

        profit = None
        profit_rate = None
        if data.selling_price is not None:
            profit = data.selling_price * data.quantity - total_cost
            if total_cost > 0:
                profit_rate = profit / total_cost

        order = Order(
            user_id=user_id,
            order_type=data.order_type,
            product_id=data.product_id,
            merchant_id=data.merchant_id,
            quantity=data.quantity,
            unit_cost=data.unit_cost,
            cost_currency=data.cost_currency,
            total_cost=total_cost,
            selling_price=data.selling_price,
            profit=profit,
            profit_rate=profit_rate,
        )
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def update_order(self, order_id: uuid.UUID, data: OrderUpdate) -> Order:
        """Update order fields; recompute profit when cost/price changes."""
        order = await self.get_order(order_id)
        update_data = data.model_dump(exclude_unset=True)

        # Handle status transition validation
        if "status" in update_data:
            new_status = update_data["status"]
            allowed = ORDER_STATUS_TRANSITIONS.get(order.status, [])
            if new_status not in allowed:
                raise ValidationException(
                    f"Cannot transition from '{order.status}' to '{new_status}'",
                    code="INVALID_STATUS_TRANSITION",
                )

        for key, value in update_data.items():
            setattr(order, key, value)

        # Recompute derived fields
        order.total_cost = float(order.unit_cost) * order.quantity
        if order.selling_price is not None:
            order.profit = (
                float(order.selling_price) * order.quantity - order.total_cost
            )
            if order.total_cost > 0:
                order.profit_rate = order.profit / order.total_cost
            else:
                order.profit_rate = None
        else:
            order.profit = None
            order.profit_rate = None

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def delete_order(self, order_id: uuid.UUID) -> None:
        """Delete an order (only drafts can be deleted)."""
        order = await self.get_order(order_id)
        if order.status != "draft":
            raise ValidationException(
                "Only draft orders can be deleted",
                code="ORDER_NOT_DELETABLE",
            )
        await self.db.delete(order)
        await self.db.flush()

    # -- Reporting (ORDER-004) --

    def _build_report_filter(
        self,
        user_id: uuid.UUID,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list:
        """Build base filter conditions for report queries."""
        conditions = [
            Order.user_id == user_id,
            Order.status.in_(["delivered", "completed"]),
        ]
        if start_date:
            conditions.append(Order.created_at >= start_date)
        if end_date:
            conditions.append(Order.created_at <= end_date)
        return conditions

    async def _get_profit_summaries(
        self, base_filter: list, period: str
    ) -> list[ProfitSummary]:
        """Fetch aggregated profit summaries grouped by time period."""
        trunc_map = {"daily": "day", "weekly": "week", "monthly": "month"}
        date_trunc = func.date_trunc(trunc_map.get(period, "month"), Order.created_at)

        query = (
            select(
                date_trunc.label("period"),
                func.sum(Order.selling_price * Order.quantity).label("total_revenue"),
                func.sum(Order.total_cost).label("total_cost"),
                func.sum(Order.profit).label("total_profit"),
                func.count(Order.id).label("order_count"),
                func.avg(Order.profit_rate).label("avg_profit_rate"),
            )
            .where(*base_filter)
            .group_by(date_trunc)
            .order_by(date_trunc.desc())
            .limit(12)
        )
        result = await self.db.execute(query)
        return [
            ProfitSummary(
                period=str(row.period),
                total_revenue=float(row.total_revenue or 0),
                total_cost=float(row.total_cost or 0),
                total_profit=float(row.total_profit or 0),
                order_count=row.order_count,
                avg_profit_rate=float(row.avg_profit_rate or 0),
            )
            for row in result.all()
        ]

    async def _get_product_rankings(self, base_filter: list) -> list[ProductRanking]:
        """Fetch top products ranked by total profit."""
        query = (
            select(
                Order.product_id,
                Product.name.label("product_name"),
                func.sum(Order.quantity).label("total_quantity"),
                func.sum(Order.profit).label("total_profit"),
                func.avg(Order.profit_rate).label("avg_profit_rate"),
            )
            .join(Product, Order.product_id == Product.id)
            .where(*base_filter)
            .group_by(Order.product_id, Product.name)
            .order_by(func.sum(Order.profit).desc())
            .limit(10)
        )
        result = await self.db.execute(query)
        return [
            ProductRanking(
                product_id=row.product_id,
                product_name=row.product_name,
                total_quantity=row.total_quantity,
                total_profit=float(row.total_profit or 0),
                avg_profit_rate=float(row.avg_profit_rate or 0),
            )
            for row in result.all()
        ]

    async def get_report(
        self,
        user_id: uuid.UUID,
        period: str = "monthly",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> ReportResponse:
        """Generate profit report with summaries and rankings."""
        base_filter = self._build_report_filter(user_id, start_date, end_date)
        summaries = await self._get_profit_summaries(base_filter, period)
        top_products = await self._get_product_rankings(base_filter)

        return ReportResponse(
            summaries=summaries,
            top_products=top_products,
        )
