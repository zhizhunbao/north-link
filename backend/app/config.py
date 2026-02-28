"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings - all values come from env vars or .env file."""

    # Application
    app_name: str = "North Link API"
    app_env: str = "development"
    app_debug: bool = True

    # Database
    database_url: str = (
        "postgresql+asyncpg://northlink:northlink@localhost:5432/northlink"
    )

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT Auth
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Exchange Rate API
    exchange_rate_api_key: str = ""

    # Encryption (AES-256 for sensitive fields)
    encryption_key: str = "dev-encryption-key-32-bytes-long!"

    # Sentry
    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
