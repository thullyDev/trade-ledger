import sqlite3

from app.db.connection import ConnectionFactory


class PositionRepository:
    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def list_positions(self, fund_id: int | None) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            if fund_id is None:
                return conn.execute(
                    """
                    SELECT fund_id, fund_code, instrument_id, instrument_code, net_quantity
                    FROM fund_positions
                    ORDER BY fund_code, instrument_code
                    """
                ).fetchall()
            return conn.execute(
                """
                SELECT fund_id, fund_code, instrument_id, instrument_code, net_quantity
                FROM fund_positions
                WHERE fund_id = ?
                ORDER BY instrument_code
                """,
                (fund_id,),
            ).fetchall()