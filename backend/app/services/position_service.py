from app.repositories.position_repository import PositionRepository
from app.schemas.common import PositionOut


class PositionService:
    def __init__(self, position_repository: PositionRepository) -> None:
        self._position_repository = position_repository

    def list_positions(self, fund_id: int | None) -> list[PositionOut]:
        rows = self._position_repository.list_positions(fund_id)
        return [
            PositionOut(
                fund_id=r["fund_id"],
                fund_code=r["fund_code"],
                instrument_id=r["instrument_id"],
                instrument_code=r["instrument_code"],
                net_quantity=float(r["net_quantity"]),
            )
            for r in rows
        ]