import { useState } from "react";
import { exportCsvUrl, patchTrade, type Fund, type Trade } from "../api/client";
import { formatDisplayDate } from "../lib/dates";
import { formatQty, formatZar } from "../lib/format";
import { ExecutedPriceModal } from "./ExecutedPriceModal";
import { StatusBadge, WorkflowSteps } from "./StatusBadge";

type Props = {
  trades: Trade[];
  funds: Fund[];
  filterDate: string;
  filterFundId: string;
  loading: boolean;
  onFilterDate: (v: string) => void;
  onFilterFundId: (v: string) => void;
  onReload: () => void;
  onError: (msg: string) => void;
};

export function TradeBlotter({
  trades,
  funds,
  filterDate,
  filterFundId,
  loading,
  onFilterDate,
  onFilterFundId,
  onReload,
  onError,
}: Props) {
  const [executing, setExecuting] = useState<Trade | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  async function advance(trade: Trade, status: string, executedPrice?: number) {
    setBusyId(trade.trade_id);
    onError("");
    try {
      const body: Record<string, unknown> = { status };
      if (status === "executed" && executedPrice != null) {
        body.executed_price = executedPrice;
      }
      await patchTrade(trade.trade_id, body);
      onReload();
    } catch (e: unknown) {
      onError(e instanceof Error ? e.message : "Update failed");
    } finally {
      setBusyId(null);
      setExecuting(null);
    }
  }

  return (
    <section className="card">
      <div className="toolbar">
        <h2>Today&apos;s trades</h2>
        <label className="field field-inline">
          <span className="field-label">Date</span>
          <input
            type="date"
            value={filterDate}
            onChange={(e) => onFilterDate(e.target.value)}
          />
          <span className="hint">{formatDisplayDate(filterDate)}</span>
        </label>
        <label className="field field-inline">
          <span className="field-label">Fund</span>
          <select value={filterFundId} onChange={(e) => onFilterFundId(e.target.value)}>
            <option value="">All funds</option>
            {funds.map((f) => (
              <option key={f.fund_id} value={f.fund_id}>
                {f.code}
              </option>
            ))}
          </select>
        </label>
        <a className="btn-secondary btn-link" href={exportCsvUrl(filterDate)}>
          Export CSV
        </a>
      </div>

      {loading && <p className="hint">Loading trades…</p>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Fund</th>
              <th>Instrument</th>
              <th>Side</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Broker</th>
              <th>Workflow</th>
              <th>Consideration</th>
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {trades.map((t) => (
              <tr
                key={t.trade_id}
                className={t.price_off_last_close ? "row-warn" : undefined}
              >
                <td>{formatDisplayDate(t.trade_date)}</td>
                <td>{t.fund_code}</td>
                <td>
                  <span className="cell-primary">{t.instrument_code}</span>
                  {t.quote_unit && <span className="meta">{t.quote_unit}</span>}
                </td>
                <td>
                  <span className={`side-tag side-${t.side}`}>{t.side}</span>
                </td>
                <td>{formatQty(t.quantity)}</td>
                <td className="price-cell">
                  {t.executed_price != null && t.executed_price !== t.order_price ? (
                    <>
                      <span className="was-price">{t.order_price}</span>
                      <strong>{t.executed_price}</strong>
                    </>
                  ) : (
                    t.order_price
                  )}
                </td>
                <td>{t.broker_name}</td>
                <td>
                  <StatusBadge status={t.status} />
                  <WorkflowSteps status={t.status} />
                </td>
                <td>{formatZar(t.consideration_zar)}</td>
                <td className="actions">
                  {t.status === "draft" && (
                    <button
                      type="button"
                      className="btn-small"
                      disabled={busyId === t.trade_id}
                      onClick={() => advance(t, "sent_to_broker")}
                    >
                      Send to broker
                    </button>
                  )}
                  {t.status === "sent_to_broker" && (
                    <button
                      type="button"
                      className="btn-small"
                      disabled={busyId === t.trade_id}
                      onClick={() => setExecuting(t)}
                    >
                      Executed
                    </button>
                  )}
                  {t.status === "executed" && (
                    <button
                      type="button"
                      className="btn-small"
                      disabled={busyId === t.trade_id}
                      onClick={() => advance(t, "done")}
                    >
                      Done
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {!loading && trades.length === 0 && (
              <tr>
                <td colSpan={10} className="empty">
                  No trades for {formatDisplayDate(filterDate)}
                  {filterFundId ? " in this fund" : ""}.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {executing && (
        <ExecutedPriceModal
          trade={executing}
          onCancel={() => setExecuting(null)}
          onConfirm={(price) => void advance(executing, "executed", price)}
        />
      )}
    </section>
  );
}