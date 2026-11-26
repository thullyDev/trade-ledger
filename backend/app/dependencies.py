from fastapi import Depends

from app.container import Container, get_container
from app.services.health_service import HealthService
from app.services.instrument_service import InstrumentService
from app.services.position_service import PositionService
from app.services.reference_service import ReferenceService
from app.services.trade_service import TradeService


def _container_dep() -> Container:
    return get_container()


def get_health_service(container: Container = Depends(_container_dep)) -> HealthService:
    return container.health_service


def get_reference_service(container: Container = Depends(_container_dep)) -> ReferenceService:
    return container.reference_service


def get_instrument_service(container: Container = Depends(_container_dep)) -> InstrumentService:
    return container.instrument_service


def get_trade_service(container: Container = Depends(_container_dep)) -> TradeService:
    return container.trade_service


def get_position_service(container: Container = Depends(_container_dep)) -> PositionService:
    return container.position_service