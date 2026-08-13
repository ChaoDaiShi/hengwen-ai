from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="HENGWEN_",
        extra="ignore",
    )

    env: Literal["development", "test", "production"] = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = "sqlite:///./storage/hengwen.db"
    storage_dir: Path = Path("./storage")
    max_file_size_mb: int = Field(default=20, gt=0)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    sse_poll_interval_seconds: float = Field(default=0.25, gt=0)
    sse_keepalive_seconds: float = Field(default=15.0, gt=0)
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
