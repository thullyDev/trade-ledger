# Trade Ledger

A small web app for the Corion Capital trading desk to capture trades before they go to the broker, instead of sending them by email. I built it as my 30 minute technical interview, using FastAPI, React with Vite, and SQLite.

What it does today:

- Capture a draft trade with date, fund, instrument, buy or sell, quantity, price and broker. Buy/sell and broker have no default, so the trader has to pick them every time.
- Search instruments loaded from the data team's market data file. The quantity label and price hint change with the instrument: shares and cents for JSE equities, nominal and percent for bonds, contracts and index points for the ALSI future, and USD for US shares.
- Show a live consideration preview and a warning when the price is more than 10% away from the last close on or before the trade date, or when there is no reference price at all.
- Move a trade through draft, sent to broker, executed and done. Marking a trade executed asks for the executed price.
- A blotter filtered by date and fund, with dates shown as dd/mm/yyyy.
- Positions per fund, as net quantity from trades marked done.
- A CSV export of the trades for a given date.

Code layout:

```text
backend/app/
  main.py          FastAPI app, registers routers under /api
  container.py     wires repositories into services
  controllers/     HTTP routes
  services/        business rules, including consideration.py and the price check
  repositories/    SQL against SQLite
backend/seed.py    applies database/NNN_*.sql in order and records them in schema_migrations
database/          001_schema.sql, 002_data.sql, the cleaned market data and DATA_ISSUES.md
frontend/src/      React app: trade form, blotter, positions panel
scripts/dev.sh     one command to seed and run everything
```

## Screen recording

Screen recording: VIDEO_LINK_HERE

## How to run it

You need Python 3.11 or newer and Node 20 or newer.

One command from the project root:

```bash
bash scripts/dev.sh
```

That creates `.venv`, installs `backend/requirements.txt`, runs `backend/seed.py` to build `trade_ledger.db` from `database/001_schema.sql` and `database/002_data.sql`, installs the frontend packages if needed, then starts both servers.

- UI: http://127.0.0.1:5173
- API docs: http://127.0.0.1:8000/docs

Or by hand:

```bash
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/seed.py
cd backend && PYTHONPATH=. uvicorn app.main:app --reload
# in a second terminal
cd frontend && npm install && npm run dev
```

The database file is not committed. `seed.py` rebuilds it, and `python backend/seed.py --dry-run` lists pending migrations without applying them.

## What I found in the market data

The data team's `market_data.sql` would not load as it was. These are the problems I found:

1. It is a SQL Server export, not a SQLite script. It uses `USE`, `GO`, `[dbo]` brackets, `NVARCHAR`, `CAST ... AS Decimal` and `SET IDENTITY_INSERT`, and the file is saved as UTF-16. DB Browser for SQLite cannot import it as is.
2. Someone added the wine co-op by hand. Its name, `Karoo Winemakers' Co-op`, has an unescaped apostrophe, so the insert for instrument 20, KWP, fails. That leaves KWP prices pointing at an instrument that does not exist.
3. The file is cut off. The last statement, the KWP close for 13 Nov, stops mid-number at `CAST(4535`.
4. KRB and NWT each have the same 2026-10-20 price row twice, even though instrument and date should be unique together.
5. HVB has two closes for 2026-11-06: the original `32634` and a `JSE EOD (corrected)` row of `33646`.
6. NMR, Namaqua Resources, has NULL closes from 9 to 13 Nov.
7. The latest prices are from 13 Nov 2026, so "last close" is stale for any trade dated after that.
8. Units are mixed. JSE equities are in cents, `ZAc`. Bonds are a percent of nominal, with a separate `AccruedPer100` column. The ALSI future is in index points with a contract size of 10. The US shares are in USD.

How the project handles them:

- I rewrote the data for SQLite in `database/001_schema.sql` and `database/002_data.sql`, saved as UTF-8 with snake_case tables. `daily_prices` has a primary key on instrument and date, a foreign key to `instruments`, and `close_price` is NOT NULL. `database/market_data_fixed.sql` keeps a cleaned SQL Server version for the data team, and `database/DATA_ISSUES.md` lists each fix.
- The KWP name is escaped, so the co-op loads as instrument 20, and its 13 Nov close is completed as 4535 cents.
- Each duplicate KRB and NWT row is dropped, keeping one.
- For HVB on 6 Nov I kept the corrected `33646` close and dropped the original.
- The NMR NULL rows are removed. The price check looks for the latest close on or before the trade date, so NMR falls back to its 6 Nov close. The data team needs to backfill those days.
- Units are handled per instrument through `quote_unit` and `asset_class`, both in the consideration maths and in the form hints.
- Stale prices are only partly handled. The check compares to the latest available close, however old it is. When the warning fires, its message includes the close date, but a price within 10% shows no date and there is no separate stale price warning. I would always show the close date and warn when it is more than a day or two old.

## What I built first and why

I started with the data, because the brief says the app must use these instruments and prices, and nothing else works until they load. Then I built the core capture loop: the schema, the trade form with the "never default buy, sell or broker" rule enforced in both the UI and the API, and the consideration calculation, because getting the money wrong is the most expensive mistake on a desk. After that came the status workflow and the price warning, then the blotter filters, positions and the CSV export.

On the backend I split controllers, services and repositories, wired together in `container.py`, so the business rules sit in one place and are easy to test and extend later. Migrations are numbered SQL files so new tables, such as status history, can be added without rebuilding the database by hand.

## Assumptions and open questions

These are the questions I would ask the desk, and the assumption I made for each one.

- **Is the bond price clean or all-in, and do we add accrued interest?** I assumed the trader types a clean price and consideration is all-in: nominal times clean plus accrued, divided by 100. Accrued comes from the latest price row on or before the trade date.
- **How far off last close should trigger the warning, 5% or 10%?** I went with 10%, `PRICE_WARN_PCT = 0.10` in `instrument_service.py`. It is a warning only and does not block the trade.
- **Do we store consideration or calculate it, and after execution is it based on the typed price or the executed price?** I calculate it on the server and store it in `consideration_zar`. Right now it is based on the order price and is recalculated when a draft is edited, but it is not recalculated when the executed price is captured. I would ask the desk, and I expect the answer is that it should use the executed price once there is one.
- **Are JSE share prices always in cents, and should consideration show in rands?** I assumed yes. Prices are typed in cents and consideration is quantity times price divided by 100, shown in rands.
- **What should happen with broken, duplicate and conflicting rows, and is the hand-added wine co-op a real instrument?** I fixed the broken SQL, kept one copy of each duplicate, trusted the corrected HVB close, dropped the NULL NMR closes and kept KWP as a normal JSE equity.
- **Can a trade go backwards or be cancelled?** I assumed it only moves forward: draft, sent to broker, executed, done. There is no cancel status. Only drafts can be edited.
- **Does commission matter yet?** I assumed not, since the notes say "later". There is no commission field.
- **What format does back office want for the end of day CSV?** The format is still to be confirmed, so I export one row per trade for the chosen date with date, fund, instrument, side, quantity, order price, executed price, broker, status and consideration.
- **Do we need to know who captured a trade before there are logins?** The schema has `created_by` and `updated_by` columns and a `users` table, but every trade is saved against a single seeded system user for now. I would add a simple captured-by name on the form until logins exist.
- **Should US shares be converted to rands?** I have no FX rates, so US share consideration is quantity times price in USD. It is stored in the same `consideration_zar` column and shown with a rand format, which is misleading. I would ask where FX rates should come from.
- **Are funds and brokers fixed?** I seeded the four funds and three brokers from the notes as reference tables with an active flag, so more can be added without code changes.

## What I would do next

- Use the executed price for consideration once a trade is executed.
- Handle FX for US shares and stop labelling USD amounts as ZAR.
- Always show the last close date next to the price and flag stale prices.
- Add a status history table for audit, and a cancel status if the desk wants one.
- Agree the end of day CSV format with back office and match it.
- Extend positions per fund with a value at last close, not just net quantity.
- Add tests, starting with the consideration maths for each asset class and the status transitions.
- Add users and login, and record the real user in `created_by` and `updated_by`.
- Add commission once the desk confirms how it works.
