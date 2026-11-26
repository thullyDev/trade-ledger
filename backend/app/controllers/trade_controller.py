from datetime import date

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies import get_trade_service
from app.schemas.trade import TradeCreate, TradeOut, TradeUpdate
from app.services.trade_service import TradeService

router = APIRouter(tags=["trades"])


@router.get("/trades", response_model=list[TradeOut])
def list_trades(
    trade_date: date | None = Query(default=None),
    fund_id: int | None = Query(default=None),
    service: TradeService = Depends(get_trade_service),
) -> list[TradeOut]:
    return service.list_trades(trade_date, fund_id)


@router.post("/trades", response_model=TradeOut, status_code=201)
def create_trade(
    payload: TradeCreate,
    service: TradeService = Depends(get_trade_service),
) -> TradeOut:
    return service.create_trade(payload)


@router.patch("/trades/{trade_id}", response_model=TradeOut)
def update_trade(
    trade_id: int,
    payload: TradeUpdate,
    service: TradeService = Depends(get_trade_service),
) -> TradeOut:
    return service.update_trade(trade_id, payload)


@router.get("/trades/export.csv")
def export_trades_csv(
    trade_date: date = Query(...),
    service: TradeService = Depends(get_trade_service),
) -> Response:
    body = service.export_csv(trade_date)
    filename = f"trades_{trade_date.isoformat()}.csv"
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )