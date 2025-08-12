"""
Configuration settings for MOVO delivery platform
إعدادات منصة MOVO للتوصيل
"""

from pydantic_settings import BaseSettings
from pydantic import AliasChoices, Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "MOVO Delivery Platform"
    version: str = "2.0.0"
    debug: bool = Field(default=True, validation_alias=AliasChoices('DEBUG', 'APP_DEBUG'))
    
    # Server settings
    host: str = "0.0.0.0"
    # Support both APP_PORT and PORT
    port: int = Field(default=8000, validation_alias=AliasChoices('APP_PORT', 'PORT'))
    
    # Database settings - PostgreSQL with async support
    # Read from DATABASE_URL
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:movo2025@localhost:5432/movo_system",
        validation_alias=AliasChoices('DATABASE_URL', 'DB_URL')
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_recycle: int = 1800
    
    # Security settings
    secret_key: str = "movo-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # AI and Analytics settings
    ai_model_path: str = "./models/"
    ai_cache_size: int = 1000
    ai_batch_size: int = 32
    ai_learning_rate: float = 0.001
    
    # Monitoring settings
    enable_monitoring: bool = True
    monitoring_interval: int = 60  # seconds
    log_level: str = Field(default="INFO", validation_alias=AliasChoices('LOG_LEVEL'))

    # App environment (dev/stage/prod)
    app_env: str = Field(default="dev", validation_alias=AliasChoices('APP_ENV', 'ENV', 'APP_ENVIRONMENT'))
    
    # External APIs
    weather_api_key: Optional[str] = None
    maps_api_key: Optional[str] = None
    payment_api_key: Optional[str] = None
    
    # Delivery settings
    delivery_fee_per_meter: float = 0.001  # SAR per meter
    max_delivery_distance: float = 50.0  # km
    free_delivery_threshold: float = 50.0  # SAR
    
    # Performance settings
    max_connections: int = 100
    request_timeout: int = 30
    cache_ttl: int = 3600
    
    # File storage
    upload_dir: str = "./uploads/"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        # Ensure we read environment from backend/.env when running from project root
        env_file = "backend/.env"
        case_sensitive = False


# Create settings instance
settings = Settings() 