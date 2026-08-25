from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_SEED = Path(__file__).resolve().parent / "data" / "seed.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", populate_by_name=True)

    allow_ticket_mutations: bool = Field(default=False, validation_alias="ALLOW_TICKET_MUTATIONS")
    seed_path: Path = Field(default=_SEED)
    host: str = "0.0.0.0"
    port: int = 8080


def get_settings() -> Settings:
    return Settings()
