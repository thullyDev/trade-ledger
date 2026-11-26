import { useState } from "react";
import { TradeBlotter } from "./components/TradeBlotter";
import { TradeForm, type PreviewInputs } from "./components/TradeForm";
import { PositionsPanel } from "./components/PositionsPanel";
import { ThemeToggle } from "./components/ThemeToggle";
import { useReferenceData } from "./hooks/useReferenceData";
import { useTheme } from "./hooks/useTheme";
import { useTradePreview } from "./hooks/useTradePreview";
import { useTrades } from "./hooks/useTrades";
import { todayIso } from "./lib/dates";
import "./app.css";

export default function App() {
  const [filterDate, setFilterDate] = useState(todayIso());
  const [filterFundId, setFilterFundId] = useState("");
  const [banner, setBanner] = useState<string | null>(null);

  const theme = useTheme();
  const reference = useReferenceData();
  const blotter = useTrades(filterDate, filterFundId);

  const [preview, setPreview] = useState<PreviewInputs>({
    formDate: todayIso(),
    formInstrumentId: "",
    formQty: "",
    formPrice: "",
  });
  const tradePreview = useTradePreview(
    preview.formInstrumentId,
    preview.formDate,
    preview.formQty,
    preview.formPrice,
  );

  const error =
    banner ?? reference.error ?? blotter.error;

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Trade Ledger</h1>
          <p className="tagline">Capture before the broker · email stops here</p>
        </div>
        <div className="topbar-actions">
          {reference.loading && <span className="pill pill-muted">Loading masters…</span>}
          <ThemeToggle mode={theme.mode} isDark={theme.isDark} onSetMode={theme.setMode} />
        </div>
      </header>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
          <button type="button" className="dismiss" onClick={() => setBanner(null)} aria-label="Dismiss">
            ×
          </button>
        </div>
      )}

      <div className="page-grid">
        <TradeForm
          funds={reference.funds}
          brokers={reference.brokers}
          instruments={reference.instruments}
          priceCheck={tradePreview.priceCheck}
          consideration={tradePreview.consideration}
          previewLoading={tradePreview.loading}
          onPreviewInputs={setPreview}
          onCreated={() => {
            setBanner(null);
            void blotter.reload();
          }}
          onError={setBanner}
        />

        <div className="stack">
          <TradeBlotter
            trades={blotter.trades}
            funds={reference.funds}
            filterDate={filterDate}
            filterFundId={filterFundId}
            loading={blotter.loading}
            onFilterDate={setFilterDate}
            onFilterFundId={setFilterFundId}
            onReload={() => void blotter.reload()}
            onError={(msg) => setBanner(msg || null)}
          />
          <PositionsPanel positions={blotter.positions} loading={blotter.loading} />
        </div>
      </div>
    </div>
  );
}