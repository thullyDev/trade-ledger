from datetime import date

import sqlite3

from app.db.connection import ConnectionFactory

_TRADE_SELECT = """
SELECT
    t.trade_id,
    t.trade_date,
    t.fund_id,
    f.code AS fund_code,
    t.instrument_id,
    i.code AS instrument_code,
    i.name AS instrument_name,
    i.quote_unit,
    t.trade_side_id,
    ts.side,
    t.quantity,
    t.order_price,
    t.executed_price,
    t.broker_id,
    b.name AS broker_name,
    t.trade_status_id,
    st.status,
    t.consideration_zar,
    t.notes
FROM trades t
JOIN funds f ON f.fund_id = t.fund_id
JOIN instruments i ON i.instrument_id = t.instrument_id
JOIN trade_side ts ON ts.trade_side_id = t.trade_side_id
JOIN brokers b ON b.broker_id = t.broker_id
JOIN trade_status st ON st.trade_status_id = t.trade_status_id
"""


class TradeRepository:
    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def list_trades(
        self,
        trade_date: date | None,
        fund_id: int | None,
    ) -> list[sqlite3.Row]:
        clauses = ["1=1"]
        params: list[object] = []
        if trade_date is not None:
            clauses.append("t.trade_date = ?")
            params.append(trade_date.isoformat())
        if fund_id is not None:
            clauses.append("t.fund_id = ?")
            params.append(fund_id)

        sql = f"{_TRADE_SELECT} WHERE {' AND '.join(clauses)} ORDER BY t.trade_id DESC"
        with self._connection_factory.connect() as conn:
            return conn.execute(sql, params).fetchall()

    def get_trade(self, trade_id: int) -> sqlite3.Row | None:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                f"{_TRADE_SELECT} WHERE t.trade_id = ?",
                (trade_id,),
            ).fetchone()

    def insert_trade(
        self,
        *,
        trade_date: str,
        fund_id: int,
        instrument_id: int,
        trade_side_id: int,
        quantity: float,
        order_price: float,
        broker_id: int,
        consideration_zar: float,
        notes: str | None,
    ) -> int:
        with self._connection_factory.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO trades (
                    trade_date, fund_id, instrument_id, trade_side_id,
                    quantity, order_price, broker_id, trade_status_id,
                    consideration_zar, notes, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 1, 1)
                """,
                (
                    trade_date,
                    fund_id,
                    instrument_id,
                    trade_side_id,
                    quantity,
                    order_price,
                    broker_id,
                    consideration_zar,
                    notes,
                ),
            )
            return int(cur.lastrowid)

    def update_trade_row(
        self,
        trade_id: int,
        fields: dict[str, object],
    ) -> bool:
        if not fields:
            return False
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [trade_id]
        with self._connection_factory.connect() as conn:
            cur = conn.execute(
                f"UPDATE trades SET {assignments}, updated_at = datetime('now') WHERE trade_id = ?",
                values,
            )
            return cur.rowcount > 0

    def get_status_id(self, status: str) -> int | None:
        with self._connection_factory.connect() as conn:
            row = conn.execute(
                "SELECT trade_status_id FROM trade_status WHERE status = ?",
                (status,),
            ).fetchone()
            return int(row["trade_status_id"]) if row else None

    def csv_rows(self, trade_date: date) -> list[sqlite3.Row]:
        with self._connection_factory.connect() as conn:
            return conn.execute(
                f"""
                {_TRADE_SELECT}
                WHERE t.trade_date = ?
                ORDER BY f.code, i.code, t.trade_id
                """,
                (trade_date.isoformat(),),
            ).fetchall()