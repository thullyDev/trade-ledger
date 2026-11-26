-- 001_schema.sql — SQLite (ERD-style: snake_case, *_id PKs, lookup tables, audit columns)
-- Usage:
--   sqlite3 trade_ledger.db < database/001_schema.sql
--   sqlite3 trade_ledger.db < database/002_data.sql

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Access (supports created_by / updated_by on domain tables)
-- ---------------------------------------------------------------------------

CREATE TABLE role (
    role_id     INTEGER PRIMARY KEY,
    role        TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL UNIQUE,
    email       TEXT,
    role_id     INTEGER NOT NULL REFERENCES role (role_id),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- Market data (reference)
-- ---------------------------------------------------------------------------

CREATE TABLE instruments (
    instrument_id   INTEGER PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT,
    asset_class     TEXT,
    exchange        TEXT,
    currency        TEXT,
    quote_unit      TEXT,
    contract_size   REAL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    created_by      INTEGER REFERENCES users (user_id),
    updated_by      INTEGER REFERENCES users (user_id)
);

CREATE TABLE daily_prices (
    instrument_id   INTEGER NOT NULL REFERENCES instruments (instrument_id),
    price_date      TEXT NOT NULL,
    close_price     REAL NOT NULL,
    accrued_per_100 REAL,
    source          TEXT,
    PRIMARY KEY (instrument_id, price_date)
);

CREATE INDEX idx_daily_prices_instrument_date ON daily_prices (instrument_id, price_date DESC);

-- ---------------------------------------------------------------------------
-- Trade capture — reference data
-- ---------------------------------------------------------------------------

CREATE TABLE funds (
    fund_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    created_by  INTEGER REFERENCES users (user_id),
    updated_by  INTEGER REFERENCES users (user_id)
);

CREATE TABLE brokers (
    broker_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    created_by  INTEGER REFERENCES users (user_id),
    updated_by  INTEGER REFERENCES users (user_id)
);

CREATE TABLE trade_status (
    trade_status_id INTEGER PRIMARY KEY,
    status          TEXT NOT NULL UNIQUE
);

CREATE TABLE trade_side (
    trade_side_id   INTEGER PRIMARY KEY,
    side            TEXT NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------------
-- Trades (central fact table)
-- ---------------------------------------------------------------------------

CREATE TABLE trades (
    trade_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date          TEXT NOT NULL,
    fund_id             INTEGER NOT NULL REFERENCES funds (fund_id),
    instrument_id       INTEGER NOT NULL REFERENCES instruments (instrument_id),
    trade_side_id       INTEGER NOT NULL REFERENCES trade_side (trade_side_id),
    quantity            REAL NOT NULL CHECK (quantity > 0),
    order_price         REAL NOT NULL,
    broker_id           INTEGER NOT NULL REFERENCES brokers (broker_id),
    trade_status_id     INTEGER NOT NULL DEFAULT 1 REFERENCES trade_status (trade_status_id),
    executed_price      REAL,
    consideration_zar   REAL,
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    created_by          INTEGER REFERENCES users (user_id),
    updated_by          INTEGER REFERENCES users (user_id),
    sent_to_broker_at   TEXT,
    executed_at         TEXT,
    completed_at        TEXT
);

CREATE INDEX idx_trades_trade_date ON trades (trade_date DESC);
CREATE INDEX idx_trades_fund_date ON trades (fund_id, trade_date DESC);
CREATE INDEX idx_trades_trade_status_id ON trades (trade_status_id);

-- ---------------------------------------------------------------------------
-- Derived views
-- ---------------------------------------------------------------------------

CREATE VIEW fund_positions AS
SELECT
    t.fund_id,
    f.code AS fund_code,
    t.instrument_id,
    i.code AS instrument_code,
    SUM(
        CASE WHEN ts.side = 'buy' THEN t.quantity ELSE -t.quantity END
    ) AS net_quantity
FROM trades t
JOIN funds f ON f.fund_id = t.fund_id
JOIN instruments i ON i.instrument_id = t.instrument_id
JOIN trade_side ts ON ts.trade_side_id = t.trade_side_id
JOIN trade_status st ON st.trade_status_id = t.trade_status_id
WHERE st.status = 'done'
GROUP BY t.fund_id, f.code, t.instrument_id, i.code
HAVING net_quantity <> 0;