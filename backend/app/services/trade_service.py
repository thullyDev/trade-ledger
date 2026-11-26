import csv
import io
from datetime import date, datetime, timezone

from fastapi import HTTPException

from app.repositories.instrument_repository import InstrumentRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.trade import TradeCreate, TradeOut, TradeUpdate
from app.services.consideration import compute_consideration_zar
from app.services.instrument_service import InstrumentService


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class TradeService:
    def __init__(
        self,
        trade_repository: TradeRepository,
        instrument_repository: InstrumentRepository,
        instrument_service: InstrumentService,
    ) -> None:
        self._trade_repository = trade_repository
        self._instrument_repository = instrument_repository
        self._instrument_service = instrument_service

    def _row_to_out(self, row) -> TradeOut:
        trade_date = date.fromisoformat(str(row["trade_date"]))
        check = self._instrument_service.price_check(
            int(row["instrument_id"]), trade_date, float(row["order_price"])
        )
        return TradeOut(
            trade_id=row["trade_id"],
            trade_date=trade_date,
            fund_id=row["fund_id"],
            fund_code=row["fund_code"],
            instrument_id=row["instrument_id"],
            instrument_code=row["instrument_code"],
            instrument_name=row["instrument_name"],
            quote_unit=row["quote_unit"],
            trade_side_id=row["trade_side_id"],
            side=row["side"],
            quantity=float(row["quantity"]),
            order_price=float(row["order_price"]),
            executed_price=float(row["executed_price"]) if row["executed_price"] is not None else None,
            broker_id=row["broker_id"],
            broker_name=row["broker_name"],
            trade_status_id=row["trade_status_id"],
            status=row["status"],
            consideration_zar=float(row["consideration_zar"]) if row["consideration_zar"] is not None else None,
            notes=row["notes"],
            price_off_last_close=check.warn if check.last_close is not None else None,
            last_close=check.last_close,
        )

    def list_trades(self, trade_date: date | None, fund_id: int | None) -> list[TradeOut]:
        rows = self._trade_repository.list_trades(trade_date, fund_id)
        return [self._row_to_out(r) for r in rows]

    def create_trade(self, payload: TradeCreate) -> TradeOut:
        instrument = self._instrument_repository.get_instrument(payload.instrument_id)
        if instrument is None:
            raise HTTPException(status_code=404, detail="Instrument not found")

        price_row = self._instrument_repository.last_close_on_or_before(
            payload.instrument_id, payload.trade_date
        )
        accrued = (
            float(price_row["accrued_per_100"])
            if price_row and price_row["accrued_per_100"] is not None
            else None
        )
        consideration, _ = compute_consideration_zar(
            asset_class=instrument["asset_class"],
            quote_unit=instrument["quote_unit"],
            contract_size=instrument["contract_size"],
            quantity=payload.quantity,
            price=payload.order_price,
            accrued_per_100=accrued,
        )

        trade_id = self._trade_repository.insert_trade(
            trade_date=payload.trade_date.isoformat(),
            fund_id=payload.fund_id,
            instrument_id=payload.instrument_id,
            trade_side_id=payload.trade_side_id,
            quantity=payload.quantity,
            order_price=payload.order_price,
            broker_id=payload.broker_id,
            consideration_zar=consideration,
            notes=payload.notes,
        )
        row = self._trade_repository.get_trade(trade_id)
        if row is None:
            raise HTTPException(status_code=500, detail="Trade not created")
        return self._row_to_out(row)

    def update_trade(self, trade_id: int, payload: TradeUpdate) -> TradeOut:
        existing = self._trade_repository.get_trade(trade_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Trade not found")

        if existing["status"] != "draft" and any(
            getattr(payload, f) is not None
            for f in (
                "trade_date",
                "fund_id",
                "instrument_id",
                "trade_side_id",
                "quantity",
                "order_price",
                "broker_id",
            )
        ):
            raise HTTPException(status_code=400, detail="Only draft trades can be edited")

        fields: dict[str, object] = {}
        for name in (
            "fund_id",
            "instrument_id",
            "trade_side_id",
            "quantity",
            "order_price",
            "broker_id",
            "notes",
        ):
            value = getattr(payload, name)
            if value is not None:
                fields[name] = value
        if payload.trade_date is not None:
            fields["trade_date"] = payload.trade_date.isoformat()

        if payload.status is not None:
            self._apply_status_transition(existing, payload, fields)

        if payload.executed_price is not None:
            fields["executed_price"] = payload.executed_price

        if any(k in fields for k in ("quantity", "order_price", "instrument_id", "trade_date")):
            self._recompute_consideration(existing, payload, fields)

        if fields:
            self._trade_repository.update_trade_row(trade_id, fields)

        row = self._trade_repository.get_trade(trade_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Trade not found")
        return self._row_to_out(row)

    def _apply_status_transition(self, existing, payload: TradeUpdate, fields: dict) -> None:
        current = existing["status"]
        target = payload.status
        allowed = {
            "draft": {"sent_to_broker"},
            "sent_to_broker": {"executed"},
            "executed": {"done"},
        }
        if target not in (allowed.get(current) or set()):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot move from {current} to {target}",
            )
        status_id = self._trade_repository.get_status_id(target)
        if status_id is None:
            raise HTTPException(status_code=500, detail="Unknown status")
        fields["trade_status_id"] = status_id

        if target == "sent_to_broker":
            fields["sent_to_broker_at"] = _now_iso()
        elif target == "executed":
            if payload.executed_price is None and existing["executed_price"] is None:
                raise HTTPException(status_code=400, detail="executed_price required")
            fields["executed_at"] = _now_iso()
            if payload.executed_price is not None:
                fields["executed_price"] = payload.executed_price
        elif target == "done":
            fields["completed_at"] = _now_iso()

    def _recompute_consideration(self, existing, payload: TradeUpdate, fields: dict) -> None:
        instrument_id = payload.instrument_id or existing["instrument_id"]
        trade_date = payload.trade_date or date.fromisoformat(str(existing["trade_date"]))
        quantity = payload.quantity or float(existing["quantity"])
        price = payload.order_price or float(existing["order_price"])

        instrument = self._instrument_repository.get_instrument(int(instrument_id))
        if instrument is None:
            raise HTTPException(status_code=404, detail="Instrument not found")

        price_row = self._instrument_repository.last_close_on_or_before(
            int(instrument_id), trade_date
        )
        accrued = (
            float(price_row["accrued_per_100"])
            if price_row and price_row["accrued_per_100"] is not None
            else None
        )
        consideration, _ = compute_consideration_zar(
            asset_class=instrument["asset_class"],
            quote_unit=instrument["quote_unit"],
            contract_size=instrument["contract_size"],
            quantity=quantity,
            price=price,
            accrued_per_100=accrued,
        )
        fields["consideration_zar"] = consideration

    def export_csv(self, trade_date: date) -> str:
        rows = self._trade_repository.csv_rows(trade_date)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "trade_date",
                "fund",
                "instrument",
                "side",
                "quantity",
                "order_price",
                "executed_price",
                "broker",
                "status",
                "consideration_zar",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r["trade_date"],
                    r["fund_code"],
                    r["instrument_code"],
                    r["side"],
                    r["quantity"],
                    r["order_price"],
                    r["executed_price"] or "",
                    r["broker_name"],
                    r["status"],
                    r["consideration_zar"] or "",
                ]
            )
        return buffer.getvalue()