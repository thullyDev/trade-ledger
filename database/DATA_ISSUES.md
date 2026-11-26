# Market data issues (original `market_data.sql`)

Cleaned copy: [`market_data_fixed.sql`](market_data_fixed.sql) (UTF-8, loadable in SQL Server).

## Data / content issues

| # | Issue | Location (approx.) | Fix applied |
|---|--------|-------------------|-------------|
| 1 | **Truncated final INSERT** — KWP `2026-11-13` row cut off at `CAST(4535` (file ends mid-statement) | Line 684 | Completed row: `4535.000000` ZAc close |
| 2 | **Invalid SQL string** — `Karoo Winemakers' Co-op` uses an unescaped apostrophe | Instrument id 20 | Escaped as `Karoo Winemakers'' Co-op` |
| 3 | **Duplicate EOD row** — KRB (id 2) two identical rows for `2026-10-20` | Lines 109–110 | Removed duplicate; kept one row |
| 4 | **Duplicate EOD row** — NWT (id 15) two identical rows for `2026-10-20` | Lines 528–529 | Removed duplicate |
| 5 | **Conflicting EOD rows** — HVB (id 3) two rows for `2026-11-06` (`32634` vs corrected `33646`) | Lines 155–156 | Dropped wrong row; kept `33646` with source `JSE EOD (corrected)` |
| 6 | **NULL closes** — NMR (id 5) `ClosePrice` NULL for `2026-11-09` through `2026-11-13` | Lines 221–225 | Rows removed (not valid once `ClosePrice` is NOT NULL). **Data team should backfill** |
| 7 | **Sparse history** — KWP only has prices from listing week (`2026-11-03` onward) | Instrument 20 | Expected for new listing; no synthetic history added |

## File / schema issues

| # | Issue | Fix applied |
|---|--------|-------------|
| 8 | **UTF-16 LE encoding** — breaks Linux/git/diff tooling | Re-exported fixed script as **UTF-8** |
| 9 | **No FOREIGN KEY** `DailyPrices` → `Instruments` | Added `FK_DailyPrices_Instruments` |
| 10 | **No UNIQUE on `Instruments.Code`** | Added `UQ_Instruments_Code` |
| 11 | **`ClosePrice` nullable** while PK rows exist with NULL price | `ClosePrice NOT NULL` on retained rows |
| 12 | **SQL Server-only** (`USE`, `GO`, brackets) | App uses **SQLite**: `001_schema.sql` + `002_data.sql` (source cleansing still in `market_data_fixed.sql`) |

## Not changed (by design)

- **Quote units** (`ZAc`, `PCT_NOMINAL`, `INDEX_POINTS`, `USD`) — used by the app for consideration and 10% price checks.
- **Bond `AccruedPer100`** — present on government/corporate bonds; equities/futures correctly NULL.
- **Weekend dates omitted** — series uses business days only (no Sat/Sun rows).

## Impact on product features

- **10% vs last close**: NMR has no official close after `2026-11-06` until backfilled — UI should warn “no reference price” as well as “>10% off last close”.
- **Positions / blotter**: instrument master and EOD file are otherwise consistent for ids 1–19 and KWP from list date.