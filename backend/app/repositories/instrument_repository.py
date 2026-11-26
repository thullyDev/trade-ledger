from datetime import date

import sqlite3

from app.db.connection import ConnectionFactory


class InstrumentRepository:
    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def list_instruments(self) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                """
                SELECT instrument_id, code, name, asset_class, quote_unit, contract_size
                FROM instruments
                ORDER BY code
                """
            ).fetchall()

    def get_instrument(self, instrument_id: int) -> sqlite3.Row | None:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                """
                SELECT instrument_id, code, name, asset_class, quote_unit, contract_size
                FROM instruments
                WHERE instrument_id = ?
                """,
                (instrument_id,),
            ).fetchone()

    def last_close_on_or_before(
        self, instrument_id: int, trade_date: date
    ) -> sqlite3.Row | None:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                """
                SELECT price_date, close_price, accrued_per_100
                FROM daily_prices
                WHERE instrument_id = ?
                  AND price_date <= ?
                ORDER BY price_date DESC
                LIMIT 1
                """,
                (instrument_id, trade_date.isoformat()),
            ).fetchone()