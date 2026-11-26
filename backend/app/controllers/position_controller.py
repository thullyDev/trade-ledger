from fastapi import APIRouter, Depends, Query

from app.dependencies import get_position_service
from app.schemas.common import PositionOut
from app.services.position_service import PositionService

router = APIRouter(tags=["positions"])


@router.get("/positions", response_model=list[PositionOut])
def list_positions(
    fund_id: int | None = Query(default=None),
    service: PositionService = Depends(get_position_service),
) -> list[PositionOut]:
    return service.list_positions(fund_id)