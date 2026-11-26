import sqlite3
from pathlib import Path

from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, health_repository: HealthRepository, database_path: Path) -> None:
        self._health_repository = health_repository
        self._database_path = database_path

    def status(self) -> dict[str, str | int | bool]:
        exists = self._database_path.is_file()
        if not exists:
            return {
                "status": "error",
                "database": str(self._database_path),
                "database_exists": False,
                "sqlite_version": sqlite3.sqlite_version,
                "migrations_applied": 0,
            }

        migrations_applied = self._health_repository.migration_count()
        return {
            "status": "ok" if migrations_applied > 0 else "error",
            "database": str(self._database_path),
            "database_exists": True,
            "sqlite_version": self._health_repository.fetch_sqlite_version(),
            "migrations_applied": migrations_applied,
        }
