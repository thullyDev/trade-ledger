"""ZAR consideration rules from business requirements."""


def compute_consideration_zar(
    *,
    asset_class: str | None,
    quote_unit: str | None,
    contract_size: float | None,
    quantity: float,
    price: float,
    accrued_per_100: float | None,
) -> tuple[float, str]:
    unit = (quote_unit or "").upper()
    asset = (asset_class or "").upper()

    if unit == "ZAC" or (asset == "EQUITY" and unit != "USD"):
        value = quantity * price / 100.0
        return round(value, 2), "equity_cents: qty × price ÷ 100"

    if unit == "PCT_NOMINAL" or asset == "BOND":
        clean = price
        accrued = accrued_per_100 or 0.0
        all_in = clean + accrued
        value = quantity * all_in / 100.0
        return round(value, 2), "bond_nominal: qty × (clean + accrued) ÷ 100"

    if unit == "INDEX_POINTS" or asset == "FUTURE":
        mult = contract_size if contract_size is not None else 10.0
        value = quantity * price * mult
        return round(value, 2), f"future: qty × price × {mult}"

    if unit == "USD":
        value = quantity * price
        return round(value, 2), "usd_equity: qty × price (USD)"

    value = quantity * price
    return round(value, 2), "default: qty × price"