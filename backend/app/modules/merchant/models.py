"""Merchant and MerchantCategory models — MERCH-001/002."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MerchantCategory(Base):
    """Merchant business category (e.g. 显卡/算力, 数码电子)."""

    __tablename__ = "merchant_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    merchants: Mapped[list["Merchant"]] = relationship(back_populates="category")


class Merchant(Base):
    """Downstream Chinese merchant — sensitive fields AES-256 encrypted."""

    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchant_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    contact_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    wechat: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    address: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    tier: Mapped[str] = mapped_column(String(10), nullable=False, default="bronze")
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category: Mapped["MerchantCategory | None"] = relationship(
        back_populates="merchants"
    )
    quotes: Mapped[list["MerchantQuote"]] = relationship(
        back_populates="merchant", cascade="all, delete-orphan"
    )


class MerchantQuote(Base):
    """Price quote from a merchant for a specific product."""

    __tablename__ = "merchant_quotes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CNY")
    quoted_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    merchant: Mapped["Merchant"] = relationship(back_populates="quotes")
