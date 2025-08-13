from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:movo2025@localhost:5432/movo_system",
        description="Async SQLAlchemy URL",
        alias="DATABASE_URL",
    )
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    class Config:
        env_file = ".env"


settings = Settings()


