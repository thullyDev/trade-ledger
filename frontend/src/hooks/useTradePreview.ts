import { useEffect, useState } from "react";
import {
  fetchConsideration,
  fetchPriceCheck,
  type ConsiderationPreview,
  type PriceCheck,
} from "../api/client";

export function useTradePreview(
  instrumentId: string,
  tradeDate: string,
  qty: string,
  price: string,
) {
  const [priceCheck, setPriceCheck] = useState<PriceCheck | null>(null);
  const [consideration, setConsideration] = useState<ConsiderationPreview | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const id = Number(instrumentId);
    const quantity = Number(qty);
    const orderPrice = Number(price);
    if (!id || !tradeDate || !quantity || !orderPrice) {
      setPriceCheck(null);
      setConsideration(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    Promise.all([
      fetchPriceCheck(id, tradeDate, orderPrice),
      fetchConsideration(id, tradeDate, quantity, orderPrice),
    ])
      .then(([pc, c]) => {
        if (!cancelled) {
          setPriceCheck(pc);
          setConsideration(c);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setPriceCheck(null);
          setConsideration(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [instrumentId, tradeDate, qty, price]);

  return { priceCheck, consideration, loading };
}