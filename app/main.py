import asyncio


async def _run():
    from app.worker_scheduler import start_worker_scheduler

    await start_worker_scheduler()
    await asyncio.Event().wait()


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    from app.workers.customer_events_exporter import CustomerEventsExporter

    asyncio.run(CustomerEventsExporter().main_worker())
