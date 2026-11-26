from pathlib import Path

from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, health_repository: HealthRepository, database_path: Path) -> None:
        self._health_repository = health_repository
        self._database_path = database_path

    def status(self) -> dict[str, str | int | bool]:
        return {
            "status": "ok",
            "database": str(self._database_path),
            "database_exists": self._database_path.is_file(),
            "sqlite_version": self._health_repository.fetch_sqlite_version(),
            "migrations_applied": self._health_repository.migration_count(),
        }