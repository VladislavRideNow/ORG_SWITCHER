import asyncio

from app.workers.customer_events_exporter import CustomerEventsExporter


if __name__ == "__main__":
    asyncio.run(CustomerEventsExporter().main_worker())

