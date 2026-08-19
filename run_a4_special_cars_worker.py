import asyncio

from app.workers.a4_special_cars_worker import A4SpecialCarsWorker


if __name__ == "__main__":
    asyncio.run(A4SpecialCarsWorker().main_worker())


