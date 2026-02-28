"""Order model — ORDER-001."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modules.logistics.models import Shipment


class Order(Base):
    """Purchase or sale order linking a product to a merchant."""

    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_created_at", "created_at"),
        Index("ix_orders_product_id", "product_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # purchase / sale
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cost_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CAD")
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    profit: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    profit_rate: Mapped[float | None] = mapped_column(
        Numeric(7, 4), nullable=True
    )  # Fixed: NUMERIC(7,4) per DB review
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    product = relationship("Product")
    merchant = relationship("Merchant")
    shipment: Mapped["Shipment | None"] = relationship(
        "Shipment", uselist=False, back_populates="order"
    )
