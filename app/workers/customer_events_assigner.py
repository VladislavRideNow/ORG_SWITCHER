import asyncio
import json
from pathlib import Path
from typing import List

from aiohttp import ClientSession

from app.adapters.ct_mobility_client import CT_MobilityClient
from app.core.logger import get_logger

logger = get_logger(__name__)


class CustomerEventsAssigner:
    def __init__(self, input_path: Path, chunk_size: int = 100):
        self.input_path = input_path
        self.chunk_size = chunk_size

    def _load_payload(self) -> List[dict]:
        with self.input_path.open("r", encoding="utf-8") as file:
            return json.load(file) or []

    @staticmethod
    def _normalize_org_ids(assign_ids: List[str]) -> List[str]:
        seen = set()
        normalized = []
        for org_id in assign_ids:
            if org_id and org_id not in seen:
                seen.add(org_id)
                normalized.append(org_id)
        return normalized

    async def main_worker(self) -> None:
        data = self._load_payload()
        logger.info("Loaded rows: %s", len(data))

        async with ClientSession() as session:
            for row in data:
                user_id = row.get("customerdataid")
                assign_ids = self._normalize_org_ids(row.get("assign_ids") or [])
                print(row)
                if not user_id or not assign_ids:
                    continue
                for i in range(0, len(assign_ids), self.chunk_size):
                    chunk = assign_ids[i : i + self.chunk_size]
                    response = await CT_MobilityClient().user_switch_org(
                        user_ids=[user_id],
                        organizations=chunk,
                        http_session=session,
                    )
                    logger.info(
                        "Assigned orgs: user=%s orgs=%s response=%s",
                        user_id,
                        chunk,
                        response,
                    )

