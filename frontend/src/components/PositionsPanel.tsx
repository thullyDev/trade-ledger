import type { Position } from "../api/client";
import { formatQty } from "../lib/format";

type Props = {
  positions: Position[];
  loading: boolean;
};

export function PositionsPanel({ positions, loading }: Props) {
  return (
    <section className="card">
      <h2>Positions by fund</h2>
      <p className="hint">Net quantity from trades marked done.</p>
      {loading && <p className="hint">Loading…</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Fund</th>
              <th>Instrument</th>
              <th>Net qty</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((p) => (
              <tr key={`${p.fund_id}-${p.instrument_id}`}>
                <td>{p.fund_code}</td>
                <td>{p.instrument_code}</td>
                <td className={p.net_quantity < 0 ? "negative" : ""}>
                  {formatQty(p.net_quantity)}
                </td>
              </tr>
            ))}
            {!loading && positions.length === 0 && (
              <tr>
                <td colSpan={3} className="empty">
                  No open positions yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}