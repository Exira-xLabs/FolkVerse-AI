from decimal import Decimal
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", extra="ignore", hide_input_in_errors=True
    )

    app_mode: Literal["demo", "live"] = "live"
    database_url: SecretStr
    session_secret: SecretStr
    cookie_secure: bool = False
    session_ttl_seconds: int = Field(default=86400, ge=60, le=604800)
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    deepseek_api_key: SecretStr | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: Literal["deepseek-flash", "deepseek-v4-pro"] = "deepseek-flash"
    guide_provider: Literal["deepseek", "ollama"] = "deepseek"
    ollama_api_key: SecretStr | None = None
    ollama_base_url: str = "https://ollama.com/v1"
    ollama_model: str = Field(default="deepseek-v4.1-flash", pattern=r"^[a-zA-Z0-9:._/-]{1,40}$")
    # Cloud subscription/account quotas use request admission, not invented token prices.
    ollama_daily_request_limit: int = Field(default=0, ge=0, le=10000)
    glm_enabled: bool = False
    trusted_lookup_enabled: bool = True
    embedding_enabled: bool = False
    embedding_model_dir: Path = ROOT / ".local/models/bge-m3"
    embedding_index_path: Path = ROOT / ".local/retrieval/bge-m3.json"
    embedding_query_timeout_seconds: float = Field(default=15, ge=0.1, le=120)
    embedding_min_cosine: float = Field(default=0.3, ge=0, le=1)
    model_max_output_tokens: int = Field(default=800, ge=1, le=4096)
    model_max_input_tokens: int = Field(default=24000, ge=512, le=64000)
    model_timeout_seconds: float = Field(default=30, ge=0.1, le=120)
    model_max_concurrency: int = Field(default=2, ge=1, le=20)
    model_rate_limit_per_minute: int = Field(default=6, ge=1, le=100)
    model_global_rate_limit_per_minute: int = Field(default=30, ge=1, le=1000)
    daily_ai_budget_usd: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    daily_ai_budget_unlimited: bool = False
    # No inferred price: exact model/base binding and positive configured rates required.
    deepseek_price_model: str | None = None
    deepseek_price_base_url: str | None = None
    deepseek_input_usd_per_million: Decimal | None = Field(default=None, gt=0, le=1000)
    deepseek_output_usd_per_million: Decimal | None = Field(default=None, gt=0, le=1000)

    @property
    def provider_key(self) -> SecretStr | None:
        return self.ollama_api_key if self.guide_provider == "ollama" else self.deepseek_api_key

    @property
    def provider_base_url(self) -> str:
        return self.ollama_base_url if self.guide_provider == "ollama" else self.deepseek_base_url

    @property
    def provider_model(self) -> str:
        return self.ollama_model if self.guide_provider == "ollama" else self.deepseek_model

    @field_validator("ollama_base_url")
    @classmethod
    def ollama_cloud_url(cls, value: str) -> str:
        if value.rstrip("/") != "https://ollama.com/v1":
            raise ValueError("OLLAMA_BASE_URL must be the official https://ollama.com/v1 endpoint")
        return value.rstrip("/")

    @field_validator("embedding_model_dir", "embedding_index_path")
    @classmethod
    def embedding_path(cls, value: Path) -> Path:
        return value if value.is_absolute() else ROOT / value

    @field_validator("deepseek_base_url")
    @classmethod
    def provider_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/", "/v1", "/v1/"}
        ):
            raise ValueError("DEEPSEEK_BASE_URL must be an HTTPS origin with optional /v1")
        return value.rstrip("/")

    @field_validator("session_secret")
    @classmethod
    def strong_session_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("SESSION_SECRET must contain at least 32 characters")
        return value

    @field_validator("database_url")
    @classmethod
    def postgres_url(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use the postgresql+psycopg driver")
        return value

    @field_validator("allowed_origins")
    @classmethod
    def concrete_origins(cls, value: list[str]) -> list[str]:
        for origin in value:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or "*" in origin
                or parsed.username
                or parsed.password
                or parsed.path
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("ALLOWED_ORIGINS must contain concrete HTTP origins")
        if not value:
            raise ValueError("ALLOWED_ORIGINS must not be empty")
        return value
