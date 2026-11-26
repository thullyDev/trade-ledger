from app.controllers.health_controller import router as health_router
from app.controllers.instrument_controller import router as instrument_router
from app.controllers.position_controller import router as position_router
from app.controllers.reference_controller import router as reference_router
from app.controllers.trade_controller import router as trade_router

__all__ = [
    "health_router",
    "reference_router",
    "instrument_router",
    "trade_router",
    "position_router",
]