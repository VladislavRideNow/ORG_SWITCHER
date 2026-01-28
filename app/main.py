import asyncio


async def _run():
    from app.worker_scheduler import start_worker_scheduler

    await start_worker_scheduler()
    await asyncio.Event().wait()


def main():
    asyncio.run(_run())
