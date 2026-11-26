import { useCallback, useEffect, useState } from "react";
import {
  fetchBrokers,
  fetchFunds,
  fetchInstruments,
  type Broker,
  type Fund,
  type Instrument,
} from "../api/client";

export function useReferenceData() {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [brokers, setBrokers] = useState<Broker[]>([]);
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [f, b, i] = await Promise.all([fetchFunds(), fetchBrokers(), fetchInstruments()]);
      setFunds(f);
      setBrokers(b);
      setInstruments(i);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load reference data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { funds, brokers, instruments, loading, error, reload };
}