"""North Link API - FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings
from app.core.middleware import setup_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register middleware (CORS, logging, error handlers)
    setup_middleware(app)

    # Health check endpoints (no auth required)
    from app.health import router as health_router

    app.include_router(health_router)

    # Register API routers
    _register_routers(app)

    return app


def _register_routers(app: FastAPI) -> None:
    """Register all module routers with the application."""
    # V1.0 routers
    from app.modules.auth.router import router as auth_router
    from app.modules.logistics.router import router as logistics_router
    from app.modules.merchant.router import router as merchant_router
    from app.modules.order.router import router as order_router
    from app.modules.price.router import router as price_router
    from app.modules.profit.router import router as profit_router
    from app.modules.recommendation.router import router as recommendation_router
    from app.modules.settings.router import router as settings_router

    app.include_router(auth_router)
    app.include_router(price_router)
    app.include_router(merchant_router)
    app.include_router(profit_router)
    app.include_router(logistics_router)
    app.include_router(recommendation_router)
    app.include_router(order_router)
    app.include_router(settings_router)

    # V1.5 routers
    from app.modules.chat.router import router as chat_router
    from app.modules.notification.router import router as notification_router
    from app.modules.scraper.router import router as scraper_router
    from app.modules.subscription.router import router as subscription_router

    app.include_router(chat_router)
    app.include_router(scraper_router)
    app.include_router(subscription_router)
    app.include_router(notification_router)


app = create_app()
