# OrgSwitcherWorker

Location: `app/workers/org_switcher_worker.py`

## Purpose

Moves new users into specific organizations based on:

- Driver license country rules.
- Age threshold rules.
- Recent creation time.

It also logs assignments to `integrations.orgswitcher_log` and sends Telegram alerts.

## Data sources

- Reads from: `DB_REPLICA` (customerdata, Order).
- Writes to: `DB_TECH` (integrations.orgswitcher_log).

## Flow

1. Initialize DB pools.
2. Query candidates for "Waiting for Payment".
3. Skip users already in `integrations.orgswitcher_log`.
4. Assign organization via CT Mobility API.
5. Insert log record + send Telegram message.
6. Repeat for "Bad Debtor" flow.
7. Shutdown DB pools.

## Schedule

Configured in `app/worker_scheduler.py`:

- Name: `org_switcher`
- Cron: every 2 minutes at second 20

## Configuration

In file:

- `WAITING_FOR_PAYMENT_CONFIG`
- `BAD_DEBTOR_CONFIG`
- `CHAT_ID`

## Manual run

Use main worker from Python:

```
python -c "import asyncio; from app.workers.org_switcher_worker import OrgSwitcherWorker; asyncio.run(OrgSwitcherWorker().main_worker())"
```

