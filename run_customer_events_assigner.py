import asyncio
from pathlib import Path

from app.workers.customer_events_assigner import CustomerEventsAssigner


if __name__ == "__main__":
    input_path = Path("output/customer_events_20260128_202420_transformed.json")
    asyncio.run(CustomerEventsAssigner(input_path=input_path).main_worker())

