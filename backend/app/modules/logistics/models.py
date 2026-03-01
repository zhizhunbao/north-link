"""FreightAgent, FreightQuote, Shipment, TrackingEvent models — LOGI-001/002."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FreightAgent(Base):
    """Freight forwarding company / logistics provider."""

    __tablename__ = "freight_agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_unit: Mapped[str] = mapped_column(String(10), nullable=False, default="kg")
    est_days_min: Mapped[int] = mapped_column(Integer, nullable=False)
    est_days_max: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pickup_service: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rating: Mapped[str] = mapped_column(String(5), nullable=False, default="B")
    contact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    quotes: Mapped[list["FreightQuote"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan"
    )
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="freight_agent")


class FreightQuote(Base):
    """Freight agent's quote for a specific product category."""

    __tablename__ = "freight_quotes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("freight_agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    est_days: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    agent: Mapped["FreightAgent"] = relationship(back_populates="quotes")


class Shipment(Base):
    """Shipment record linking an order to a freight agent."""

    __tablename__ = "shipments"
    __table_args__ = (UniqueConstraint("order_id", name="uq_shipments_order_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
    )
    freight_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("freight_agents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipping_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tariff_cost: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    clearance_fee: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    order = relationship("Order", back_populates="shipment")
    freight_agent: Mapped["FreightAgent"] = relationship(back_populates="shipments")
    tracking_events: Mapped[list["TrackingEvent"]] = relationship(
        back_populates="shipment", cascade="all, delete-orphan"
    )


class TrackingEvent(Base):
    """Single tracking event in a shipment's timeline."""

    __tablename__ = "tracking_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    shipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shipments.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    shipment: Mapped["Shipment"] = relationship(back_populates="tracking_events")
