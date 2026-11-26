# Trade ledger — frontend overview (from requirements)

## Purpose

Replace email trade capture with a blotter: capture trades **before** the broker, show workflow status, and support back-office export.

## Core screens

### 1. Today’s trades (home)

- Table: trade date (**dd/mm/yyyy**), fund, instrument (code + name), buy/sell, qty, price, broker, status, consideration (ZAR).
- Default filter: **today**; fund dropdown (all | KESCON | FYNBAL | BAOGLB | PROINC).
- Status badges: **Draft** → **Sent to broker** → **Executed** → **Done**.
- If `executed_price` ≠ `order_price`, show both (e.g. strikethrough order, bold executed).

### 2. New / edit trade (form)

Required explicit choices (no defaults):

| Field | UI rule |
|-------|---------|
| Date | Date picker, display dd/mm/yyyy |
| Fund | Dropdown from `GET /api/funds` |
| Instrument | Searchable dropdown from market data (+ metadata: asset class, quote unit) |
| Buy / Sell | Two radio buttons or toggle — **empty until user picks** |
| Qty | Number; label “Nominal” for bonds, “Contracts” for futures, “Shares” for equity |
| Price | Number; hint from `quote_unit` (cents for JSE, % for bonds, points for ALSIZ26) |
| Broker | Dropdown from `GET /api/brokers` — **no default** |

Actions:

- **Save draft**
- **Send to broker** (draft → sent)
- Back office: **Mark executed** (capture executed price) → **Done**

### 3. Price sanity (inline)

On price blur or before send:

- Load **last close** for instrument from `DailyPrices` (latest date ≤ trade date).
- If \(\|price - lastClose\| / lastClose > 10\%\), show **warning** (allow override with note).
- If no last close (e.g. NMR gap, brand-new KWP), show **“No reference price”**.

### 4. Consideration (read-only, from API)

Display backend-computed ZAR:

| Asset class | Rule |
|-------------|------|
| JSE equity | `qty × price / 100` (price in cents) |
| Bond | `nominal × (clean + accrued) / 100` — accrued from EOD for trade date |
| Future | `contracts × points × 10` (use `contract_size` from instrument) |
| USD equity | qty × price in USD (FX later if needed) |

### 5. Positions per fund (stretch)

- View: fund selector → table instrument, net qty, optional mark from last close.
- Driven by `fund_positions` view (status = `done`).

### 6. EOD CSV export

- Button: “Export today’s trades (CSV)” for back office — column layout TBC.

## API surface (backend)

| Method | Path | Use |
|--------|------|-----|
| GET | `/api/funds` | Fund dropdown |
| GET | `/api/brokers` | Broker dropdown |
| GET | `/api/trade-sides` | Buy / sell lookup (`trade_side_id`) |
| GET | `/api/trade-statuses` | Workflow labels (`trade_status_id`) |
| GET | `/api/instruments` | Instrument search |
| GET | `/api/instruments/:id/last-close?date=` | 10% check |
| GET | `/api/trades?date=&fund=` | Today’s list |
| POST | `/api/trades` | Create draft |
| PATCH | `/api/trades/:id` | Update + status transitions |
| GET | `/api/trades/export.csv?date=` | Back office |

## Data dependencies

- Create DB: `sqlite3 trade_ledger.db < database/001_schema.sql`
- Load data: `sqlite3 trade_ledger.db < database/002_data.sql` (instruments, EOD prices, funds, brokers)