from fastapi import APIRouter, Depends

from app.dependencies import get_reference_service
from app.schemas.common import BrokerOut, FundOut, LookupOut
from app.services.reference_service import ReferenceService

router = APIRouter(tags=["reference"])


@router.get("/funds", response_model=list[FundOut])
def list_funds(service: ReferenceService = Depends(get_reference_service)) -> list[FundOut]:
    return service.list_funds()


@router.get("/brokers", response_model=list[BrokerOut])
def list_brokers(service: ReferenceService = Depends(get_reference_service)) -> list[BrokerOut]:
    return service.list_brokers()


@router.get("/trade-sides", response_model=list[LookupOut])
def list_trade_sides(service: ReferenceService = Depends(get_reference_service)) -> list[LookupOut]:
    return service.list_trade_sides()


@router.get("/trade-statuses", response_model=list[LookupOut])
def list_trade_statuses(
    service: ReferenceService = Depends(get_reference_service),
) -> list[LookupOut]:
    return service.list_trade_statuses()