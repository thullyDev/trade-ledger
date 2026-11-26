import { useCallback, useEffect, useState } from "react";
import { fetchPositions, fetchTrades, type Position, type Trade } from "../api/client";

export function useTrades(filterDate: string, filterFundId: string) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const fundId = filterFundId ? Number(filterFundId) : undefined;
      const [t, p] = await Promise.all([
        fetchTrades({ trade_date: filterDate, fund_id: fundId }),
        fetchPositions(fundId),
      ]);
      setTrades(t);
      setPositions(p);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load trades");
    } finally {
      setLoading(false);
    }
  }, [filterDate, filterFundId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { trades, positions, loading, error, reload };
}