from pydantic import BaseModel, ConfigDict


class FundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fund_id: int
    code: str
    name: str


class BrokerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    broker_id: int
    name: str


class InstrumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    instrument_id: int
    code: str
    name: str | None
    asset_class: str | None
    quote_unit: str | None
    contract_size: float | None


class LookupOut(BaseModel):
    id: int
    label: str


class PositionOut(BaseModel):
    fund_id: int
    fund_code: str
    instrument_id: int
    instrument_code: str
    net_quantity: float