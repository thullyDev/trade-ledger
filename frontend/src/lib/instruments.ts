import type { Instrument } from "../api/client";

export function qtyLabel(instrument: Instrument | undefined): string {
  const asset = instrument?.asset_class?.toUpperCase();
  if (asset === "BOND") return "Nominal";
  if (asset === "FUTURE") return "Contracts";
  return "Shares";
}

export function priceHint(instrument: Instrument | undefined): string {
  if (!instrument?.quote_unit) return "Enter price";
  switch (instrument.quote_unit) {
    case "ZAc":
      return "JSE equity — price in cents (ZAc)";
    case "PCT_NOMINAL":
      return "Bond — clean price as % of nominal";
    case "INDEX_POINTS":
      return `Future — index points (× ${instrument.contract_size ?? 10})`;
    case "USD":
      return "USD per share";
    default:
      return `Unit: ${instrument.quote_unit}`;
  }
}

export function filterInstruments(instruments: Instrument[], query: string): Instrument[] {
  const q = query.trim().toLowerCase();
  if (!q) return instruments;
  return instruments.filter(
    (i) =>
      i.code.toLowerCase().includes(q) ||
      (i.name?.toLowerCase().includes(q) ?? false) ||
      (i.asset_class?.toLowerCase().includes(q) ?? false),
  );
}