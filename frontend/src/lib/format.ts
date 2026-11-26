export function formatZar(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR",
    minimumFractionDigits: 2,
  }).format(value);
}

export function formatQty(value: number): string {
  return new Intl.NumberFormat("en-ZA", { maximumFractionDigits: 4 }).format(value);
}

export function parseApiError(text: string): string {
  try {
    const json = JSON.parse(text) as { detail?: string | { msg: string }[] };
    if (typeof json.detail === "string") return json.detail;
    if (Array.isArray(json.detail)) {
      return json.detail.map((d) => d.msg).join("; ");
    }
  } catch {
    /* plain text */
  }
  return text.length > 200 ? `${text.slice(0, 200)}…` : text;
}