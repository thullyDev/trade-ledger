from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TradeCreate(BaseModel):
    trade_date: date
    fund_id: int
    instrument_id: int
    trade_side_id: int = Field(..., description="Required — no default buy/sell")
    quantity: float = Field(..., gt=0)
    order_price: float = Field(..., gt=0)
    broker_id: int = Field(..., description="Required — no default broker")
    notes: str | None = None

    @field_validator("trade_side_id")
    @classmethod
    def side_must_be_explicit(cls, v: int) -> int:
        if v not in (1, 2):
            raise ValueError("trade_side_id must be 1 (buy) or 2 (sell)")
        return v


class TradeUpdate(BaseModel):
    trade_date: date | None = None
    fund_id: int | None = None
    instrument_id: int | None = None
    trade_side_id: int | None = None
    quantity: float | None = Field(default=None, gt=0)
    order_price: float | None = Field(default=None, gt=0)
    broker_id: int | None = None
    executed_price: float | None = Field(default=None, gt=0)
    notes: str | None = None
    status: Literal["sent_to_broker", "executed", "done"] | None = None


class TradeOut(BaseModel):
    trade_id: int
    trade_date: date
    fund_id: int
    fund_code: str
    instrument_id: int
    instrument_code: str
    instrument_name: str | None
    quote_unit: str | None
    trade_side_id: int
    side: str
    quantity: float
    order_price: float
    executed_price: float | None
    broker_id: int
    broker_name: str
    trade_status_id: int
    status: str
    consideration_zar: float | None
    notes: str | None
    price_off_last_close: bool | None = None
    last_close: float | None = None


class PriceCheckOut(BaseModel):
    instrument_id: int
    trade_date: date
    price: float
    last_close: float | None
    last_close_date: date | None
    pct_from_close: float | None
    warn: bool
    message: str | None


class ConsiderationPreview(BaseModel):
    consideration_zar: float
    method: str