from datetime import date

from fastapi import HTTPException

from app.repositories.instrument_repository import InstrumentRepository
from app.schemas.common import InstrumentOut
from app.schemas.trade import ConsiderationPreview, PriceCheckOut
from app.services.consideration import compute_consideration_zar

PRICE_WARN_PCT = 0.10


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository) -> None:
        self._instrument_repository = instrument_repository

    def list_instruments(self) -> list[InstrumentOut]:
        rows = self._instrument_repository.list_instruments()
        return [
            InstrumentOut(
                instrument_id=r["instrument_id"],
                code=r["code"],
                name=r["name"],
                asset_class=r["asset_class"],
                quote_unit=r["quote_unit"],
                contract_size=r["contract_size"],
            )
            for r in rows
        ]

    def price_check(self, instrument_id: int, trade_date: date, price: float) -> PriceCheckOut:
        row = self._instrument_repository.last_close_on_or_before(instrument_id, trade_date)
        if row is None:
            return PriceCheckOut(
                instrument_id=instrument_id,
                trade_date=trade_date,
                price=price,
                last_close=None,
                last_close_date=None,
                pct_from_close=None,
                warn=True,
                message="No reference price on or before trade date",
            )

        last_close = float(row["close_price"])
        last_close_date = date.fromisoformat(str(row["price_date"]))
        pct = abs(price - last_close) / last_close if last_close else None
        warn = pct is not None and pct > PRICE_WARN_PCT
        message = None
        if warn:
            message = f"Price is {pct * 100:.1f}% off last close ({last_close:.4f} on {last_close_date.isoformat()})"

        return PriceCheckOut(
            instrument_id=instrument_id,
            trade_date=trade_date,
            price=price,
            last_close=last_close,
            last_close_date=last_close_date,
            pct_from_close=round(pct, 4) if pct is not None else None,
            warn=warn,
            message=message,
        )

    def preview_consideration(
        self,
        instrument_id: int,
        trade_date: date,
        quantity: float,
        price: float,
    ) -> ConsiderationPreview:
        instrument = self._instrument_repository.get_instrument(instrument_id)
        if instrument is None:
            raise HTTPException(status_code=404, detail="Instrument not found")

        price_row = self._instrument_repository.last_close_on_or_before(instrument_id, trade_date)
        accrued = float(price_row["accrued_per_100"]) if price_row and price_row["accrued_per_100"] else None

        value, method = compute_consideration_zar(
            asset_class=instrument["asset_class"],
            quote_unit=instrument["quote_unit"],
            contract_size=instrument["contract_size"],
            quantity=quantity,
            price=price,
            accrued_per_100=accrued,
        )
        return ConsiderationPreview(consideration_zar=value, method=method)