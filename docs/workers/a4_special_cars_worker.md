# A4SpecialCarsWorker

Location: `app/workers/a4_special_cars_worker.py`

## Purpose

Assigns organization "A4 Special cars" to users that:

- Have EU driver license country.
- Are older than 25.
- Have total run sum > 200.
- Do not already have A4 in `customerdata__2__organization`.

It logs assignments to `integrations.a4_special_cars_log` and sends a Telegram summary.

## Data sources

- Reads from: `DB_REPLICA` (customerdata, Order, customerdata__2__organization).
- Writes to: `DB_TECH` (integrations.a4_special_cars_log).

## Flow

1. Initialize DB pools.
2. Query candidates from `customerdata` + `Order`.
3. Query existing A4 members from `customerdata__2__organization`.
4. Filter candidates by ID (compare `c.id` to `customerdataid`).
5. Assign org via CT Mobility API (batched by 100).
6. Log each assignment and send Telegram summary.
7. Shutdown DB pools.

## Schedule

Configured in `app/worker_scheduler.py`:

- Name: `a4_special_cars`
- Cron: daily at 02:00 Asia/Nicosia

## Configuration

In file:

- `SPECIAL_CARS_ORG_ID`
- `EU_LICENSE_COUNTRIES`
- `CHAT_ID`

## Manual run

```
python run_a4_special_cars_worker.py
```


