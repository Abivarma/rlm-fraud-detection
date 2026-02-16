"""Application configuration and settings."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    openai_api_key: str = Field(..., description="OpenAI API key")
    anthropic_api_key: str | None = Field(None, description="Anthropic API key (optional)")

    # LLM Configuration
    main_model: str = Field(default="openai:gpt-4o", description="Main LLM model")
    sub_model: str = Field(default="openai:gpt-4o-mini", description="Sub-model for RLM")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_detection"
    )
    database_url_sync: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/fraud_detection"
    )

    # Embedding Configuration
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)

    # Application
    app_name: str = Field(default="Fraud Detection RLM System")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"]
    )

    # Performance Limits
    max_transactions_naive: int = Field(default=50, description="Max transactions for naive LLM")
    max_transactions_rag: int = Field(default=100, description="Max transactions for RAG")
    max_transactions_rlm: int = Field(
        default=10000, description="Max transactions for RLM (large context)"
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60)

    # Dataset
    kaggle_dataset_path: str = Field(default="./data/creditcard.csv")
    dataset_url: str = Field(
        default="https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
