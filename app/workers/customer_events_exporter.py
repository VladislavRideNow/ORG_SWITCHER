import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from aiohttp import ClientSession

from app import config as settings
from app.core.database import DB_REPLICA, initialize_db, shutdown_db
from app.core.logger import get_logger

logger = get_logger(__name__)

TARGET_INITIATOR = "Sukhov Vladislav RIDENOW"
TARGET_DESCRIPTIONS = (
    "Новое значение: A1 Regular clients",
    "New value: A1 Regular clients",
)


class CustomerEventsExporter:
    def __init__(
        self,
        from_ts: float = 1769288400,
        to_ts: float = 1769633999.999,
        count: int = 15,
        concurrency: int = 10,
    ):
        self.base_url = settings.MAIN_HOST
        self.session_id = settings.CARTREK_SESSION_ID
        self.from_ts = from_ts
        self.to_ts = to_ts
        self.count = count
        self.semaphore = asyncio.Semaphore(concurrency)

    @staticmethod
    def _normalize_event(event: dict) -> dict:
        return {
            "EventDateTime": event.get("EventDateTime"),
            "EventDateTimeStr": event.get("EventDateTimeStr"),
            "EventType": event.get("EventType"),
            "EventName": event.get("EventName"),
            "ObjectId": event.get("ObjectId"),
            "ObjectName": event.get("ObjectName"),
            "InitiatorId": event.get("InitiatorId"),
            "InitiatorName": event.get("InitiatorName"),
            "Description": event.get("Description"),
            "AlarmType": event.get("AlarmType"),
        }

    @staticmethod
    def _extract_events(payload) -> List[dict]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("events", "Events", "data", "Data"):
                if key in payload and isinstance(payload[key], list):
                    return payload[key]
        return []

    async def _get_customer_ids(self) -> List[str]:
        rows = await DB_REPLICA.execute_query_get_data(
            query="""
                select id as customerdataid
                from customerdata
                limit 100
            """
        )
        rows = rows or []
        return [str(row["customerdataid"]) for row in rows]

    def _headers(self) -> dict:
        if not self.session_id and not settings.CARTREK_SESSID:
            raise RuntimeError("CARTREK_SESSION_ID is not set in environment")
        headers = {
            "Content-Type": "application/json",
        }
        if self.session_id:
            headers["cartrek-sessionid"] = self.session_id
        if settings.CARTREK_SESSID:
            headers["Cookie"] = f"sessid={settings.CARTREK_SESSID}"
        return headers

    async def _fetch_events(self, session: ClientSession, customerdataid: str) -> List[dict]:
        url = f"{self.base_url}/admin/events/customer"
        payload = {
            "objectId": customerdataid,
            "count": self.count,
            "lastEventTimes": [],
            "fromDate": self.from_ts,
            "toDate": self.to_ts,
        }
        async with self.semaphore:
            async with session.post(url, json=payload, headers=self._headers()) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.warning(
                        "Events request failed: id=%s status=%s body=%s",
                        customerdataid,
                        response.status,
                        text,
                    )
                    print(f"[DEBUG] response status for {customerdataid}: {response.status}")
                    print(f"[DEBUG] response body for {customerdataid}: {text}")
                    return []
                logger.debug("Events request ok: id=%s", customerdataid)
                text = await response.text()
                print(f"[DEBUG] response status for {customerdataid}: {response.status}")
                print(f"[DEBUG] response body for {customerdataid}: {text}")
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    return []
                return self._extract_events(data)

    @staticmethod
    def _filter_events(events: Iterable[dict]) -> List[dict]:
        filtered = []
        for event in events:
            if "InitiatorName" not in event or "Description" not in event:
                continue
            initiator = (event["InitiatorName"] or "").strip()
            if initiator != TARGET_INITIATOR:
                continue
            description = event["Description"] or ""
            # Normalize whitespace to avoid non-breaking spaces or double spaces
            normalized = " ".join(description.replace("\u00a0", " ").split())
            if any(token in normalized for token in TARGET_DESCRIPTIONS):
                filtered.append(event)
        return filtered

    async def _collect_for_user(self, session: ClientSession, customerdataid: str) -> Optional[dict]:
        events = await self._fetch_events(session, customerdataid)
        matches = self._filter_events(events)
        if not matches:
            if events:
                print(f"[DEBUG] no match for {customerdataid}, events: {events}")
            return None
        return {
            "customerdataid": customerdataid,
            "events": [self._normalize_event(e) for e in matches],
        }

    async def main_worker(self) -> Path:
        await initialize_db()
        logger.info("Customer events export started.")

        customer_ids = await self._get_customer_ids()
        logger.info("Customer ids loaded: %s", len(customer_ids))

        results: List[dict] = []
        processed = 0
        matched = 0
        total = len(customer_ids)
        log_every = 50
        async with ClientSession() as session:
            tasks = [
                self._collect_for_user(session=session, customerdataid=customerdataid)
                for customerdataid in customer_ids
            ]
            for task in asyncio.as_completed(tasks):
                item = await task
                processed += 1
                if item:
                    matched += 1
                    results.append(item)
                if processed % log_every == 0 or processed == total:
                    logger.info(
                        "Progress: %s/%s processed, %s matched",
                        processed,
                        total,
                        matched,
                    )

        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"customer_events_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = output_dir / filename

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=2)

        logger.info("Export finished. Saved %s records to %s", len(results), output_path)
        await shutdown_db()
        return output_path

