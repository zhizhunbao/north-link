"""ScraperTask and SocialPost ORM models - BE-007."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScraperTask(Base):
    """Record of a data scraping task execution."""

    __tablename__ = "scraper_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    keywords: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    items_found: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    social_posts: Mapped[list["SocialPost"]] = relationship(
        back_populates="scraper_task"
    )

    __table_args__ = (
        Index("ix_scraper_tasks_trigger", "trigger_type", "trigger_id"),
        Index("ix_scraper_tasks_platform", "platform"),
        Index("ix_scraper_tasks_status", "status"),
        Index("ix_scraper_tasks_created_at", "created_at"),
    )


class SocialPost(Base):
    """Social media post scraped from platforms like Xiaohongshu, Douyin."""

    __tablename__ = "social_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scraper_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scraper_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    post_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(100), nullable=True)
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    post_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    scraper_task: Mapped["ScraperTask | None"] = relationship(
        back_populates="social_posts"
    )

    __table_args__ = (
        Index(
            "uq_social_posts_platform_post_id",
            "platform",
            "post_id",
            unique=True,
        ),
        Index("ix_social_posts_scraper_task_id", "scraper_task_id"),
        Index("ix_social_posts_platform", "platform"),
    )
