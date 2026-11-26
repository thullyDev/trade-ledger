from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_instrument_service
from app.schemas.common import InstrumentOut
from app.schemas.trade import ConsiderationPreview, PriceCheckOut
from app.services.instrument_service import InstrumentService

router = APIRouter(tags=["instruments"])


@router.get("/instruments", response_model=list[InstrumentOut])
def list_instruments(
    service: InstrumentService = Depends(get_instrument_service),
) -> list[InstrumentOut]:
    return service.list_instruments()


@router.get("/instruments/{instrument_id}/price-check", response_model=PriceCheckOut)
def price_check(
    instrument_id: int,
    trade_date: date = Query(...),
    price: float = Query(..., gt=0),
    service: InstrumentService = Depends(get_instrument_service),
) -> PriceCheckOut:
    return service.price_check(instrument_id, trade_date, price)


@router.get("/instruments/{instrument_id}/consideration", response_model=ConsiderationPreview)
def preview_consideration(
    instrument_id: int,
    trade_date: date = Query(...),
    quantity: float = Query(..., gt=0),
    price: float = Query(..., gt=0),
    service: InstrumentService = Depends(get_instrument_service),
) -> ConsiderationPreview:
    return service.preview_consideration(instrument_id, trade_date, quantity, price)