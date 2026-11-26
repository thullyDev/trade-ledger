# Database (SQLite)

Schema follows the same conventions as the NMA reference ERD:

- **snake_case** table and column names  
- **`{entity}_id`** primary keys  
- **Lookup tables** for enums (`role`, `trade_status`, `trade_side`) instead of hard-coded CHECK lists on facts  
- **Audit columns** on domain tables: `created_at`, `updated_at`, `created_by`, `updated_by`  
- **Central fact table** `trades` with FKs to reference entities  

## Load

Preferred (tracks applied files for future `003_*.sql`, …):

```bash
python backend/seed.py
```

Manual:

```bash
sqlite3 trade_ledger.db < database/001_schema.sql
sqlite3 trade_ledger.db < database/002_data.sql
```

## ERD (HTML)

Open in a browser: [`database/erd.html`](erd.html) — SVG diagram plus column cheat sheets.

## Entity map (Mermaid)

```mermaid
erDiagram
    role ||--o{ users : has
    users ||--o{ trades : "created_by"
    users ||--o{ funds : audits
    users ||--o{ brokers : audits

    funds ||--o{ trades : ""
    brokers ||--o{ trades : ""
    instruments ||--o{ trades : ""
    instruments ||--o{ daily_prices : ""
    trade_side ||--o{ trades : ""
    trade_status ||--o{ trades : ""

    role {
        int role_id PK
        text role UK
    }

    users {
        int user_id PK
        text username UK
        text email
        int role_id FK
        text created_at
        text updated_at
    }

    instruments {
        int instrument_id PK
        text code UK
        text asset_class
        text quote_unit
        real contract_size
    }

    daily_prices {
        int instrument_id PK,FK
        text price_date PK
        real close_price
        real accrued_per_100
    }

    funds {
        int fund_id PK
        text code UK
        text name
    }

    brokers {
        int broker_id PK
        text name UK
    }

    trade_status {
        int trade_status_id PK
        text status UK
    }

    trade_side {
        int trade_side_id PK
        text side UK
    }

    trades {
        int trade_id PK
        text trade_date
        int fund_id FK
        int instrument_id FK
        int trade_side_id FK
        int broker_id FK
        int trade_status_id FK
        real quantity
        real order_price
        real executed_price
        real consideration_zar
    }
```

`002_data.sql` order: **role → users → lookups → instruments → daily_prices → funds → brokers**