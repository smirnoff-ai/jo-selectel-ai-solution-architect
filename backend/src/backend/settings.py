from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_REPO_ENV, extra="ignore")

    openai_api_key: SecretStr
    openai_base_url: str
    openai_model: str
    langfuse_public_key: str
    langfuse_secret_key: SecretStr
    langfuse_host: str
    database_url: str
    session_secret: SecretStr
    dispatcher_login: str
    dispatcher_password: SecretStr
    mock_severholod_url: str
    ping_database: bool = Field(default=True)
    ensure_schema: bool = Field(default=True)
    use_agent: bool = Field(default=True)
    agent_timeout_seconds: int = Field(default=90)
    host: str = "0.0.0.0"
    port: int = 8000


def get_settings() -> Settings:
    return Settings()
