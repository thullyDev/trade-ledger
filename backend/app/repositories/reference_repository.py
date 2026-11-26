import sqlite3

from app.db.connection import ConnectionFactory


class ReferenceRepository:
    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def list_active_funds(self) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                """
                SELECT fund_id, code, name
                FROM funds
                WHERE is_active = 1
                ORDER BY code
                """
            ).fetchall()

    def list_active_brokers(self) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                """
                SELECT broker_id, name
                FROM brokers
                WHERE is_active = 1
                ORDER BY name
                """
            ).fetchall()

    def list_trade_sides(self) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                "SELECT trade_side_id, side FROM trade_side ORDER BY trade_side_id"
            ).fetchall()

    def list_trade_statuses(self) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                "SELECT trade_status_id, status FROM trade_status ORDER BY trade_status_id"
            ).fetchall()