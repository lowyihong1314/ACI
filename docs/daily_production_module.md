# Raw Data Production Module

This module is now driven entirely by 3 Excel workbooks stored in the project root:

- [Daily Total Tonnage 2026(1).xlsx](/home/utba/flaskapp/ACI/Daily%20Total%20Tonnage%202026(1).xlsx)
- [Total Monthly Tonnage 2026(1).xlsx](/home/utba/flaskapp/ACI/Total%20Monthly%20Tonnage%202026(1).xlsx)
- [PLAN 2026(1).xlsx](/home/utba/flaskapp/ACI/PLAN%202026(1).xlsx)

## Scope

- Product master from workbook rows
- Daily product tonnage by product and warehouse
- Monthly product tonnage
- Daily machine planning
- Monthly machine actual summary
- Monthly efficiency summary
- Full database rebuild from the 3 source workbooks

## Core backend models

- [product.py](/home/utba/flaskapp/ACI/backend/models/product.py)
- [daily_product_tonnage.py](/home/utba/flaskapp/ACI/backend/models/daily_product_tonnage.py)
- [monthly_product_tonnage.py](/home/utba/flaskapp/ACI/backend/models/monthly_product_tonnage.py)
- [daily_machine_plan.py](/home/utba/flaskapp/ACI/backend/models/daily_machine_plan.py)
- [monthly_machine_summary.py](/home/utba/flaskapp/ACI/backend/models/monthly_machine_summary.py)
- [monthly_efficiency_summary.py](/home/utba/flaskapp/ACI/backend/models/monthly_efficiency_summary.py)

## Import script

- [import_raw_excel_data.py](/home/utba/flaskapp/ACI/backend/scripts/import_raw_excel_data.py)

This script clears raw-data tables and reloads them from the 3 workbook files.

Run manually:

```bash
cd /home/utba/flaskapp/ACI/backend
. .venv/bin/activate
python scripts/import_raw_excel_data.py
```

## Migrations

Relevant revisions:

- `20260317_0003` create raw-data tables
- `20260317_0004` drop legacy production tables
- `20260317_0005` normalize machine codes for workbook import
- `20260317_0006` expand `product.part_code`
- `20260317_0007` make product uniqueness `part_code + warehouse_code`

Apply:

```bash
cd /home/utba/flaskapp/ACI/backend
. .venv/bin/activate
alembic upgrade head
```

## Active API

### Master data

- `GET /api/plants`
- `GET /api/machines`
- `POST /api/machines`
- `PUT /api/machines/<id>`
- `GET /api/manage-machine`
- `POST /api/manage-machine`
- `PUT /api/manage-machine/<id>`
- `GET /api/products`
- `POST /api/products`
- `PUT /api/products/<id>`

### Daily raw data

- `GET /api/daily-production?date=YYYY-MM-DD`
- `GET /api/daily-production?month=YYYY-MM`
- `POST /api/daily-production`
- `PUT /api/daily-production/<id>`
- `DELETE /api/daily-production/<id>`
- `GET /api/daily-machine-plans?date=YYYY-MM-DD`
- `GET /api/daily-machine-plans?month=YYYY-MM`
- `POST /api/daily-machine-plans`
- `PUT /api/daily-machine-plans/<id>`
- `DELETE /api/daily-machine-plans/<id>`

### Reports

- `GET /api/reports/monthly-machine-summary?month=YYYY-MM`
- `GET /api/reports/monthly-plant-summary?month=YYYY-MM`
- `GET /api/reports/ytd-summary?year=YYYY&month=MM`

### Raw data rebuild

- `GET /api/raw-data/summary`
- `POST /api/raw-data/import`

## Legacy endpoints

These are intentionally deprecated and return `410`:

- `/api/breakdown-reasons`
- `/api/daily-breakdowns`
- `/api/annual-targets`
- `/api/reports/breakdown-analysis`

## Frontend sections

The SPA now exposes:

- `Dashboard`
- `Raw Data Admin`
- `Profile`

Inside `Raw Data Admin`:

- `Daily Product Output`
- `Daily Machine Plan`
- `Monthly Summary`
- `Manage Machine`
- `Products`
- `Raw Data Import`
