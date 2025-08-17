try:
    from pydantic_settings import BaseSettings
except Exception:  # fallback if pydantic v1
    from pydantic import BaseSettings  # type: ignore
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:movo2025@localhost:5432/movo_system"
    )
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()



