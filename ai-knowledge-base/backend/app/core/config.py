from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-knowledge-base"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/knowledge"
    embedding_dim: int = 1536

    upload_dir: Path = Path("/app/data/uploads")
    max_upload_size_bytes: int = 10 * 1024 * 1024
    allowed_content_types: tuple[str, ...] = ("text/plain", "application/pdf")

    chunk_size: int = 1000
    chunk_overlap: int = 150

    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
