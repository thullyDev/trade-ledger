#!/usr/bin/env python3
"""Apply numbered SQL migrations in database/ in sequence.

Naming: NNN_description.sql (e.g. 001_schema.sql, 002_data.sql).
Tracks applied files in schema_migrations so new scripts run as the project grows.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

MIGRATION_PATTERN = re.compile(r"^(\d{3})_.+\.sql$")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def list_migrations(migrations_dir: Path) -> list[Path]:
    if not migrations_dir.is_dir():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    files = [
        path
        for path in migrations_dir.iterdir()
        if path.is_file() and MIGRATION_PATTERN.match(path.name)
    ]
    return sorted(files, key=lambda p: p.name)


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename   TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )


def applied_migrations(conn: sqlite3.Connection) -> set[str]:
    ensure_migrations_table(conn)
    rows = conn.execute("SELECT filename FROM schema_migrations").fetchall()
    return {str(row[0]) for row in rows}


def run_script(conn: sqlite3.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)


def seed(database_path: Path, migrations_dir: Path, dry_run: bool = False) -> int:
    migrations = list_migrations(migrations_dir)
    if not migrations:
        print(f"No migration files matching NNN_*.sql in {migrations_dir}")
        return 0

    database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        done = applied_migrations(conn)
        pending = [m for m in migrations if m.name not in done]

        if not pending:
            print(f"Database up to date ({len(done)} migration(s)): {database_path}")
            return 0

        print(f"Database: {database_path}")
        for path in pending:
            if dry_run:
                print(f"  [dry-run] would apply {path.name}")
                continue
            print(f"  applying {path.name} ...")
            run_script(conn, path)
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (?)",
                (path.name,),
            )
            conn.commit()
            print(f"  applied {path.name}")

        if dry_run:
            conn.rollback()
        else:
            print(f"Done. {len(pending)} migration(s) applied.")
    finally:
        conn.close()

    return 0


def main() -> int:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=root / "trade_ledger.db",
        help="SQLite database file path",
    )
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=root / "database",
        help="Directory containing NNN_*.sql files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List pending migrations without applying",
    )
    args = parser.parse_args()

    try:
        return seed(args.database, args.migrations_dir, dry_run=args.dry_run)
    except Exception as exc:
        print(f"seed failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())