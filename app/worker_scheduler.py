from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.logger import get_logger
from app.workers.org_switcher_worker import OrgSwitcherWorker

logger = get_logger(__name__)
scheduler = AsyncIOScheduler()


def setup_jobs():
    jobs = [
        {
            "name": "org_switcher",
            "func": OrgSwitcherWorker().main_worker,
            "cron": {"minute": "*/2", "second": 20},
        },
    ]

    for job in jobs:
        scheduler.add_job(
            job["func"],
            trigger="cron",
            name=job["name"],
            **job["cron"],
        )

        if job.get("run_on_startup"):
            scheduler.add_job(
                job["func"],
                trigger="date",
                name=f"{job['name']}_startup_run",
            )


async def start_worker_scheduler():
    setup_jobs()
    if not scheduler.running:
        scheduler.start()
        logger.info("Worker scheduler started.")


async def stop_worker_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Worker scheduler stopped.")

