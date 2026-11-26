# Trade Ledger

A small web app for capturing trades before they go to the broker, built with FastAPI, React, and SQLite for a Corion Capital interview.

## Quick start

```bash
git clone https://github.com/thullyDev/trade-ledger.git && cd trade-ledger && bash scripts/dev.sh
```

This creates the environment, seeds the database, and starts both servers.

- UI: http://127.0.0.1:5173
- API docs: http://127.0.0.1:8000/docs

## Screen recording

https://drive.google.com/file/d/1jDlrqb02zgp5cIC0YN6daPJTLj2u20uw/view

## Features

- Capture a trade with date, fund, instrument, buy or sell, quantity, price, and broker. Buy, sell, and broker have no default, so you pick them every time.
- Search instruments loaded from the market data. Quantity and price hints change with the instrument: shares and cents for JSE equities, nominal and percent for bonds, contracts and index points for the ALSI future, and USD for US shares.
- Live consideration preview, and a warning when the price is more than 10% away from the last close, or when there is no reference price.
- Move a trade through draft, sent to broker, executed, and done. Marking a trade executed asks for the executed price.
- A blotter filtered by date and fund, with dates shown as dd/mm/yyyy.
- Positions per fund, as net quantity from trades marked done.
- A CSV export of the trades for a given date.

## Prerequisites

- Python 3, tested with 3.13.5
- Node.js, tested with 24.22.1

## Setup

```bash
git clone https://github.com/thullyDev/trade-ledger
cd trade-ledger
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/seed.py
cd frontend && npm install
```

On Windows, activate the virtual environment with:

```bat
.venv\Scripts\activate
```

The database lives at the project root as `trade_ledger.db`. `backend/seed.py` builds it from `database/001_schema.sql` and `database/002_data.sql`. The database file is not committed.

## Run

From the project root, activate the virtual environment first. On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bat
.venv\Scripts\activate
```

Backend:

```bash
cd backend && PYTHONPATH=. uvicorn app.main:app --reload
```

Frontend, in a second terminal:

```bash
cd frontend && npm run dev
```

If you start the backend in a new terminal, activate the virtual environment in that terminal first.

- UI: http://127.0.0.1:5173
- API docs: http://127.0.0.1:8000/docs

## Project layout

- `backend/` — FastAPI app
- `backend/seed.py` — applies numbered SQL files in `database/` and records them in schema_migrations
- `database/` — schema and cleaned market data
- `frontend/` — React and Vite UI

## My thoughts and questions

The market data file would not load as it was. It is a UTF-16 SQL Server T-SQL export and uses GO, so it is not a SQLite script. I rewrote it for SQLite in the database folder.

Someone added the wine co-op by hand. The name Karoo Winemakers' Co-op has an unescaped apostrophe, so the KWP instrument never inserts and its prices have no instrument. The file is also cut off at the KWP close for 13 Nov.

KRB and NWT each have the same price row twice on 20 Oct 2026. HVB has two closes on 6 Nov 2026, and I kept the corrected JSE EOD close. NMR has no closes from 9 to 13 Nov, so the price check falls back to an older close. Prices stop on 13 Nov 2026, so last close is stale for any later trade date.

Units are mixed. JSE shares are in cents, ZAc. Bonds are a percent of nominal plus AccruedPer100. The ALSI future is in index points with a contract size of 10. US shares are in USD.

A few things I would ask a colleague, and what I would do next:

Should consideration use the executed price once a trade is filled? Right now I save it from the order price and I do not recalculate it after execution.

Where should FX rates come from for US shares? I store those amounts in USD in the consideration_zar column, with no conversion, which is misleading.

The 10% price warning can quietly use an older close when a later one is missing or the file has run out. Should we always show the close date, and warn when that date is stale?

Should a trade be cancellable, or only move forward? Status only goes draft, sent to broker, executed, then done. There is no cancel, and only drafts can be edited.

There is one seeded system user and no captured-by field on the form. Should we record who booked the trade before logins exist?

Commission is not in the app yet. Does the desk want that now, or later?
