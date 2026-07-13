from functools import lru_cache

from pydantic import Field, PostgresDsn, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore unknown variables
    )

    # === Database ===
    DATABASE_URL: PostgresDsn = Field(
        description="PostgreSQL connection URL"
    )

    # === Ollama / LLM ===
    OLLAMA_BASE_URL: AnyHttpUrl = Field(
        description="Base URL of Ollama API"
    )

    LLM_MODEL: str = Field(
        description="Model name for generation"
    )

    LLM_TEMPERATURE: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Generation temperature (0.0-1.0)"
    )

    LLM_MAX_TOKENS: int = Field(
        default=2048,
        gt=0,
        description="Maximum number of tokens in response"
    )

    # === LangSmith ===
    LANGSMITH_TRACING: bool = Field(
        default=False,
        description="Enable LangSmith tracing"
    )

    LANGSMITH_API_KEY: str | None = Field(
        default=None,
        description="LangSmith API key"
    )

    LANGSMITH_PROJECT: str = Field(
        default="support-ai",
        description="LangSmith project name"
    )

    LANGSMITH_WORKSPACE_ID: str | None = Field(
        default=None,
        description="LangSmith workspace"
    )

    LANGSMITH_ENDPOINT: str | None = Field(
        default=None,
        description="Endpoint for LangSmith tracing"
    )

    # === Application ===
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000, gt=0, lt=65536)
    APP_ENV: str = Field(default="dev", pattern="^(dev|prod)$")

    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for tokens (min. 32 characters)"
    )

    # === Telegram ===
    TELEGRAM_BOT_TOKEN: str | None = Field(default=None)
    TELEGRAM_CHAT_ID: str | None = Field(default=None)
    ALERT_PRIORITY_THRESHOLD: str = Field(default="critical")

    # === Security ===
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        gt=0,
        description="Requests per minute limit per user"
    )

    # === Convenience properties ===
    @property
    def is_dev(self) -> bool:
        """Returns True if the application is running in development mode."""
        return self.APP_ENV == "dev"

    @property
    def ollama_model_url(self) -> str:
        """Full URL for calling the model in Ollama."""
        return f"{self.OLLAMA_BASE_URL}/api/generate"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of settings.

    lru_cache ensures that settings are loaded once
    and reused throughout the application.
    """
    return Settings()