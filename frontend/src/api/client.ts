export type Fund = { fund_id: number; code: string; name: string };
export type Broker = { broker_id: number; name: string };
export type Lookup = { id: number; label: string };
export type Instrument = {
  instrument_id: number;
  code: string;
  name: string | null;
  asset_class: string | null;
  quote_unit: string | null;
  contract_size: number | null;
};

export type Trade = {
  trade_id: number;
  trade_date: string;
  fund_id: number;
  fund_code: string;
  instrument_id: number;
  instrument_code: string;
  instrument_name: string | null;
  quote_unit: string | null;
  trade_side_id: number;
  side: string;
  quantity: number;
  order_price: number;
  executed_price: number | null;
  broker_id: number;
  broker_name: string;
  trade_status_id: number;
  status: string;
  consideration_zar: number | null;
  notes: string | null;
  price_off_last_close: boolean | null;
  last_close: number | null;
};

export type PriceCheck = {
  warn: boolean;
  message: string | null;
  last_close: number | null;
};

export type ConsiderationPreview = {
  consideration_zar: number;
  method: string;
};

export type Position = {
  fund_id: number;
  fund_code: string;
  instrument_id: number;
  instrument_code: string;
  net_quantity: number;
};

const base = import.meta.env.VITE_API_BASE_URL ?? "";

import { parseApiError } from "../lib/format";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(parseApiError(text || `HTTP ${res.status}`));
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const fetchFunds = () => api<Fund[]>("/api/funds");
export const fetchBrokers = () => api<Broker[]>("/api/brokers");
export const fetchInstruments = () => api<Instrument[]>("/api/instruments");
export const fetchTrades = (params: { trade_date?: string; fund_id?: number }) => {
  const q = new URLSearchParams();
  if (params.trade_date) q.set("trade_date", params.trade_date);
  if (params.fund_id) q.set("fund_id", String(params.fund_id));
  const qs = q.toString();
  return api<Trade[]>(`/api/trades${qs ? `?${qs}` : ""}`);
};
export const createTrade = (body: unknown) =>
  api<Trade>("/api/trades", { method: "POST", body: JSON.stringify(body) });
export const patchTrade = (id: number, body: unknown) =>
  api<Trade>(`/api/trades/${id}`, { method: "PATCH", body: JSON.stringify(body) });
export const fetchPriceCheck = (instrumentId: number, tradeDate: string, price: number) =>
  api<PriceCheck>(
    `/api/instruments/${instrumentId}/price-check?trade_date=${tradeDate}&price=${price}`,
  );
export const fetchConsideration = (
  instrumentId: number,
  tradeDate: string,
  quantity: number,
  price: number,
) =>
  api<ConsiderationPreview>(
    `/api/instruments/${instrumentId}/consideration?trade_date=${tradeDate}&quantity=${quantity}&price=${price}`,
  );
export const fetchPositions = (fundId?: number) => {
  const q = fundId ? `?fund_id=${fundId}` : "";
  return api<Position[]>(`/api/positions${q}`);
};

export function exportCsvUrl(tradeDate: string): string {
  return `${base}/api/trades/export.csv?trade_date=${tradeDate}`;
}