from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """All runtime configuration, read from environment variables or `.env`."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    pinecone_api_key: str = ""
    pinecone_index: str = "it-helpdesk"
    pinecone_namespace: str = "kb"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    kb_dir: Path = PROJECT_ROOT / "data" / "kb"
    tickets_file: Path = PROJECT_ROOT / "data" / "tickets" / "tickets.jsonl"

    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 4
    # Cosine similarity; text-embedding-3-* relevant KB matches scored 0.48-0.66 in testing.
    score_threshold: float = 0.45
    memory_max_turns: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()
