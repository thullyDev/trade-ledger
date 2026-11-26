import { FormEvent, useEffect, useState } from "react";
import { createTrade, type Broker, type ConsiderationPreview, type Fund, type Instrument, type PriceCheck } from "../api/client";
import { formatDisplayDate, todayIso } from "../lib/dates";
import { formatZar } from "../lib/format";
import { priceHint, qtyLabel } from "../lib/instruments";
import { InstrumentSearch } from "./InstrumentSearch";
import { SideToggle } from "./SideToggle";

type SideChoice = "" | "1" | "2";

type Props = {
  funds: Fund[];
  brokers: Broker[];
  instruments: Instrument[];
  onCreated: () => void;
  onError: (msg: string) => void;
  priceCheck: PriceCheck | null;
  consideration: ConsiderationPreview | null;
  previewLoading: boolean;
  onPreviewInputs: (state: PreviewInputs) => void;
};

export type PreviewInputs = {
  formDate: string;
  formInstrumentId: string;
  formQty: string;
  formPrice: string;
};

export function TradeForm({
  funds,
  brokers,
  instruments,
  onCreated,
  onError,
  priceCheck,
  consideration,
  previewLoading,
  onPreviewInputs,
}: Props) {
  const [formDate, setFormDate] = useState(todayIso());
  const [formFundId, setFormFundId] = useState("");
  const [formInstrumentId, setFormInstrumentId] = useState("");
  const [formSideId, setFormSideId] = useState<SideChoice>("");
  const [formBrokerId, setFormBrokerId] = useState("");
  const [formQty, setFormQty] = useState("");
  const [formPrice, setFormPrice] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const selected = instruments.find((i) => i.instrument_id === Number(formInstrumentId));

  useEffect(() => {
    onPreviewInputs({
      formDate,
      formInstrumentId,
      formQty,
      formPrice,
    });
  }, [formDate, formInstrumentId, formQty, formPrice, onPreviewInputs]);

  function syncPreview(
    date: string,
    instrumentId: string,
    qty: string,
    price: string,
  ) {
    onPreviewInputs({ formDate: date, formInstrumentId: instrumentId, formQty: qty, formPrice: price });
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!formSideId) {
      onError("Select buy or sell before saving");
      return;
    }
    if (!formBrokerId) {
      onError("Select a broker before saving");
      return;
    }
    setSubmitting(true);
    try {
      await createTrade({
        trade_date: formDate,
        fund_id: Number(formFundId),
        instrument_id: Number(formInstrumentId),
        trade_side_id: Number(formSideId),
        quantity: Number(formQty),
        order_price: Number(formPrice),
        broker_id: Number(formBrokerId),
      });
      setFormSideId("");
      setFormBrokerId("");
      setFormQty("");
      setFormPrice("");
      onCreated();
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : "Create failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="card card-accent">
      <div className="card-head">
        <h2>New trade</h2>
        <span className="pill">Draft only</span>
      </div>

      <form className="form-grid" onSubmit={onSubmit}>
        <label className="field">
          <span className="field-label">Date</span>
          <input
            type="date"
            value={formDate}
            onChange={(ev) => {
              setFormDate(ev.target.value);
              syncPreview(ev.target.value, formInstrumentId, formQty, formPrice);
            }}
            required
          />
          <span className="hint display-date">{formatDisplayDate(formDate)}</span>
        </label>

        <label className="field">
          <span className="field-label">Fund</span>
          <select
            value={formFundId}
            onChange={(ev) => setFormFundId(ev.target.value)}
            required
          >
            <option value="">Choose fund…</option>
            {funds.map((f) => (
              <option key={f.fund_id} value={f.fund_id}>
                {f.code} — {f.name}
              </option>
            ))}
          </select>
        </label>

        <div className="field-wide">
          <InstrumentSearch
            instruments={instruments}
            value={formInstrumentId}
            onChange={(id) => {
              setFormInstrumentId(id);
              syncPreview(formDate, id, formQty, formPrice);
            }}
            required
          />
        </div>

        <SideToggle value={formSideId} onChange={setFormSideId} />

        <label className="field">
          <span className="field-label">{qtyLabel(selected)}</span>
          <input
            type="number"
            min="0"
            step="any"
            value={formQty}
            onChange={(ev) => {
              setFormQty(ev.target.value);
              syncPreview(formDate, formInstrumentId, ev.target.value, formPrice);
            }}
            required
          />
        </label>

        <label className="field">
          <span className="field-label">Price</span>
          <input
            type="number"
            min="0"
            step="any"
            value={formPrice}
            onChange={(ev) => {
              setFormPrice(ev.target.value);
              syncPreview(formDate, formInstrumentId, formQty, ev.target.value);
            }}
            required
          />
          <span className="hint">{priceHint(selected)}</span>
        </label>

        <label className="field">
          <span className="field-label">Broker</span>
          <select
            value={formBrokerId}
            onChange={(ev) => setFormBrokerId(ev.target.value)}
            required
          >
            <option value="">Choose broker…</option>
            {brokers.map((b) => (
              <option key={b.broker_id} value={b.broker_id}>
                {b.name}
              </option>
            ))}
          </select>
          <span className="hint">No default — pick every time</span>
        </label>

        <div className="preview-panel field-wide">
          {previewLoading && <p className="hint">Updating consideration…</p>}
          {priceCheck?.warn && (
            <p className="alert alert-warn" role="status">
              {priceCheck.message ?? "Price more than 10% off last close"}
            </p>
          )}
          {priceCheck && !priceCheck.warn && priceCheck.last_close != null && (
            <p className="hint">
              Last close: {priceCheck.last_close} (within 10%)
            </p>
          )}
          {consideration && (
            <p className="consideration-line">
              Consideration{" "}
              <strong>{formatZar(consideration.consideration_zar)}</strong>
              <span className="hint"> — {consideration.method}</span>
            </p>
          )}
        </div>

        <div className="form-actions field-wide">
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? "Saving…" : "Save draft"}
          </button>
        </div>
      </form>
    </section>
  );
}