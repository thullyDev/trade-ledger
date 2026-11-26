from app.repositories.reference_repository import ReferenceRepository
from app.schemas.common import BrokerOut, FundOut, LookupOut


class ReferenceService:
    def __init__(self, reference_repository: ReferenceRepository) -> None:
        self._reference_repository = reference_repository

    def list_funds(self) -> list[FundOut]:
        rows = self._reference_repository.list_active_funds()
        return [FundOut(fund_id=r["fund_id"], code=r["code"], name=r["name"]) for r in rows]

    def list_brokers(self) -> list[BrokerOut]:
        rows = self._reference_repository.list_active_brokers()
        return [BrokerOut(broker_id=r["broker_id"], name=r["name"]) for r in rows]

    def list_trade_sides(self) -> list[LookupOut]:
        rows = self._reference_repository.list_trade_sides()
        return [LookupOut(id=r["trade_side_id"], label=r["side"]) for r in rows]

    def list_trade_statuses(self) -> list[LookupOut]:
        rows = self._reference_repository.list_trade_statuses()
        return [LookupOut(id=r["trade_status_id"], label=r["status"]) for r in rows]