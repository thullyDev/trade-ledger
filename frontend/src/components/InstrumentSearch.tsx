import { type ReactNode, useMemo, useState } from "react";
import type { Instrument } from "../api/client";
import { filterInstruments } from "../lib/instruments";

type Props = {
  instruments: Instrument[];
  value: string;
  onChange: (instrumentId: string) => void;
  required?: boolean;
};

export function InstrumentSearch({ instruments, value, onChange, required }: Props) {
  const [query, setQuery] = useState("");
  const selected = instruments.find((i) => i.instrument_id === Number(value));

  const matches = useMemo(() => filterInstruments(instruments, query).slice(0, 8), [
    instruments,
    query,
  ]);

  return (
    <div className="instrument-search">
      <label className="field">
        <span className="field-label">Instrument</span>
        {selected ? (
          <Button
            type="button"
            className="selected-instrument"
            onClick={() => {
              onChange("");
              setQuery("");
            }}
          >
            <strong>{selected.code}</strong>
            <span>{selected.name}</span>
            <span className="meta">
              {selected.asset_class} · {selected.quote_unit}
            </span>
            <span className="change-hint">Change</span>
          </Button>
        ) : (
          <>
            <input
              type="search"
              placeholder="Search code or name…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoComplete="off"
              required={required && !value}
            />
            {query && matches.length > 0 && (
              <ul className="search-results" role="listbox">
                {matches.map((i) => (
                  <li key={i.instrument_id}>
                    <button
                      type="button"
                      role="option"
                      onClick={() => {
                        onChange(String(i.instrument_id));
                        setQuery("");
                      }}
                    >
                      <strong>{i.code}</strong>
                      <span>{i.name}</span>
                      <span className="meta">{i.asset_class}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {query && matches.length === 0 && (
              <p className="hint">No instruments match “{query}”.</p>
            )}
          </>
        )}
      </label>
    </div>
  );
}

function Button({
  type,
  className,
  onClick,
  children,
}: {
  type: "button";
  className?: string;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button type={type} className={className} onClick={onClick}>
      {children}
    </button>
  );
}