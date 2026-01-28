# ORG Switcher Workers

This project runs scheduled background workers for CT Mobility using APScheduler.
Each worker is a separate module under `app/workers` and is registered in
`app/worker_scheduler.py`.

## Structure

- `app/main.py`: Application entrypoint (starts scheduler).
- `app/worker_scheduler.py`: Central scheduler that registers all workers.
- `app/workers/`: Worker implementations.
- `app/adapters/`: External integrations (CT Mobility, Telegram).
- `app/core/`: Shared infra (database, logger).

## Requirements

- Python 3.11
- Postgres access (replica + tech DB)
- CT Mobility API key
- Telegram bot token

## Environment variables

Loaded from `.env` by `app/config.py`:

- `REPL_DB`, `REPL_USER`, `REPL_HOST`, `REPL_PASS`, `REPL_PORT`
- `TECH_DB`, `TECH_USER`, `TECH_HOST`, `TECH_PASS`, `TECH_PORT`
- `CT_API_KEY_CAR_CONTROL`, `CT_MAIN_HOST`
- `CAR_BOT_TOKEN`

## Run

Run the scheduler:

```
python main.py
```

Run a single worker (example):

```
python run_a4_special_cars_worker.py
```

## Workers

- `OrgSwitcherWorker` — `app/workers/org_switcher_worker.py`
- `A4SpecialCarsWorker` — `app/workers/a4_special_cars_worker.py`

Detailed docs:

- `docs/workers/org_switcher_worker.md`
- `docs/workers/a4_special_cars_worker.md`

