"""Application composition root (wires repos → services for injection)."""

from app.config import Settings
from app.db.connection import ConnectionFactory
from app.repositories.health_repository import HealthRepository
from app.repositories.instrument_repository import InstrumentRepository
from app.repositories.position_repository import PositionRepository
from app.repositories.reference_repository import ReferenceRepository
from app.repositories.trade_repository import TradeRepository
from app.services.health_service import HealthService
from app.services.instrument_service import InstrumentService
from app.services.position_service import PositionService
from app.services.reference_service import ReferenceService
from app.services.trade_service import TradeService


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.connection_factory = ConnectionFactory(settings.database_path)

        self.health_repository = HealthRepository(self.connection_factory)
        self.reference_repository = ReferenceRepository(self.connection_factory)
        self.instrument_repository = InstrumentRepository(self.connection_factory)
        self.trade_repository = TradeRepository(self.connection_factory)
        self.position_repository = PositionRepository(self.connection_factory)

        self.health_service = HealthService(
            self.health_repository,
            settings.database_path,
        )
        self.reference_service = ReferenceService(self.reference_repository)
        self.instrument_service = InstrumentService(self.instrument_repository)
        self.trade_service = TradeService(
            self.trade_repository,
            self.instrument_repository,
            self.instrument_service,
        )
        self.position_service = PositionService(self.position_repository)


_container: Container | None = None


def init_container(settings: Settings) -> Container:
    global _container
    _container = Container(settings)
    return _container


def get_container() -> Container:
    if _container is None:
        raise RuntimeError("Container not initialized; call init_container() in app lifespan")
    return _container