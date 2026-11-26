import sqlite3

from app.db.connection import ConnectionFactory


class HealthRepository:
    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def fetch_sqlite_version(self) -> str:
        with self._connection_factory.connect() as conn:
            row = conn.execute("SELECT sqlite_version() AS version").fetchone()
            if row is None:
                raise RuntimeError("sqlite_version query returned no row")
            return str(row["version"])

    def migration_count(self) -> int:
        with self._connection_factory.connect() as conn:
            if not self._table_exists(conn, "schema_migrations"):
                return 0
            row = conn.execute("SELECT COUNT(*) AS n FROM schema_migrations").fetchone()
            return int(row["n"]) if row else 0

    @staticmethod
    def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (name,),
        ).fetchone()
        return row is not None