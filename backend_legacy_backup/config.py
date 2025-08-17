"""
Backend unified settings (single source, supports Pydantic v1/v2).
- أضفنا BACKEND_CORS_ORIGINS لاستخدامه مع CORS.
"""

# محاولة دعم Pydantic v2 أولاً، ثم الرجوع لـ v1 إن لزم
try:
    from pydantic_settings import BaseSettings  # pydantic v2
    from pydantic import AliasChoices, Field
except ImportError:  # fallback for pydantic v1
    from pydantic import BaseSettings  # type: ignore
    from pydantic import Field  # type: ignore
    try:
        from pydantic import AliasChoices  # type: ignore
    except Exception:  # pydantic v1 قد لا يدعم AliasChoices
        AliasChoices = lambda *args, **kwargs: None  # type: ignore

from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Application settings
    app_name: str = "MOVO Delivery Platform"
    version: str = "2.0.0"
    debug: bool = Field(default=True, validation_alias=AliasChoices('DEBUG', 'APP_DEBUG'))

    # Server settings
    host: str = "0.0.0.0"
    port: int = Field(default=8000, validation_alias=AliasChoices('APP_PORT', 'PORT'))

    # Database settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:movo2025@localhost:5432/movo_system",
        validation_alias=AliasChoices('DATABASE_URL', 'DB_URL')
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_recycle: int = 1800

    # Security
    secret_key: str = "movo-secret-key-change-in-production"
    access_token_expire_minutes: int = 30

    # AI and Analytics
    ai_model_path: str = "./models/"
    ai_cache_size: int = 1000
    ai_batch_size: int = 32
    ai_learning_rate: float = 0.001

    # Monitoring
    enable_monitoring: bool = True
    monitoring_interval: int = 60
    log_level: str = Field(default="INFO", validation_alias=AliasChoices('LOG_LEVEL'))

    # Environment
    app_env: str = Field(default="dev", validation_alias=AliasChoices('APP_ENV', 'ENV', 'APP_ENVIRONMENT'))

    # External APIs
    weather_api_key: Optional[str] = None
    maps_api_key: Optional[str] = None
    payment_api_key: Optional[str] = None

    # Delivery
    delivery_fee_per_meter: float = 0.001
    max_delivery_distance: float = 50.0
    free_delivery_threshold: float = 50.0

    # Performance
    max_connections: int = 100
    request_timeout: int = 30
    cache_ttl: int = 3600

    # File storage
    upload_dir: str = "./uploads/"
    max_file_size: int = 10 * 1024 * 1024

    class Config:
        # قراءة البيئة من الجذر أو backend/.env
        env_file = ".env"
        case_sensitive = False


# Create settings instance (مطلوب لاستخدامه عبر باقي النظام)
settings = Settings()