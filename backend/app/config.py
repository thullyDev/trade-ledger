from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_under_project_root(path: Path) -> Path:
    if not path.is_absolute():
        return (_PROJECT_ROOT / path).resolve()
    return path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_path: Path = _PROJECT_ROOT / "trade_ledger.db"
    migrations_dir: Path = _PROJECT_ROOT / "database"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]

    @field_validator("database_path", mode="after")
    @classmethod
    def database_path_under_project_root(cls, value: Path) -> Path:
        return resolve_under_project_root(value)


def get_settings() -> Settings:
    return Settings()
