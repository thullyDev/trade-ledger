import { FormEvent, useState } from "react";
import type { Trade } from "../api/client";
import { formatDisplayDate } from "../lib/dates";

type Props = {
  trade: Trade;
  onConfirm: (executedPrice: number) => void;
  onCancel: () => void;
};

export function ExecutedPriceModal({ trade, onConfirm, onCancel }: Props) {
  const [value, setValue] = useState(String(trade.order_price));

  function submit(e: FormEvent) {
    e.preventDefault();
    const n = Number(value);
    if (n > 0) onConfirm(n);
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onCancel}>
      <div
        className="modal"
        role="dialog"
        aria-labelledby="exec-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 id="exec-title">Mark executed</h3>
        <p className="modal-sub">
          {trade.instrument_code} · {trade.side} · order {trade.order_price}
          {trade.quote_unit ? ` ${trade.quote_unit}` : ""}
        </p>
        <form onSubmit={submit}>
          <label className="field">
            <span className="field-label">Executed price</span>
            <input
              type="number"
              step="any"
              min="0"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              autoFocus
              required
            />
            {Number(value) !== trade.order_price && (
              <span className="hint warn-inline">
                Differs from typed price ({trade.order_price}) — shown on blotter
              </span>
            )}
          </label>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save executed
            </button>
          </div>
        </form>
        <p className="hint">Trade date: {formatDisplayDate(trade.trade_date)}</p>
      </div>
    </div>
  );
}