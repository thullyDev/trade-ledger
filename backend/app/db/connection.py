import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


class ConnectionFactory:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def get_connection(factory: ConnectionFactory) -> Generator[sqlite3.Connection, None, None]:
    with factory.connect() as conn:
        yield conn