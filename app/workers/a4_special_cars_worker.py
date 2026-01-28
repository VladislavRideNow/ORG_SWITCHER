from datetime import date, datetime

from aiohttp import ClientSession

from app.adapters.ct_mobility_client import CT_MobilityClient
from app.adapters.tg_bot import TG_BOT
from app.core.database import DB_REPLICA, DB_TECH, initialize_db, shutdown_db
from app.core.logger import get_logger

logger = get_logger(__name__)

SPECIAL_CARS_ORG_ID = "d41a9561-3d2d-40a1-99b1-b0ee013eaad3"
CHAT_ID = -954331597

EU_LICENSE_COUNTRIES = [
    "AUT",
    "BEL",
    "BGR",
    "HRV",
    "CYP",
    "CZE",
    "DNK",
    "EST",
    "FIN",
    "FRA",
    "DEU",
    "GRC",
    "HUN",
    "IRL",
    "ITA",
    "LVA",
    "LTU",
    "LUX",
    "MLT",
    "NLD",
    "POL",
    "PRT",
    "ROU",
    "SVK",
    "SVN",
    "ESP",
    "SWE",
    "CYP",
]


class A4SpecialCarsWorker:
    @staticmethod
    def _normalize_user_id(value) -> str:
        return str(value).strip().lower()

    @staticmethod
    def _calc_age(birthdate: date) -> int:
        today = date.today()
        return today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )

    async def _get_candidates(self):
        return await DB_REPLICA.execute_query_get_data(
            query=f"""
                select
                    c.userid,
                    c.id,
                    c.driverslicencecountry,
                    c.birthdate,
                    sum(o.totalrun) as totalrun_sum
                from customerdata c
                left join "Order" o
                    on o.customerid = c.userid
                where
                    (c.rating >= 0 or c.rating is null)
                    and c.driverslicencecountry in (
                        {", ".join(f"'{code}'" for code in EU_LICENSE_COUNTRIES)}
                    )
                    and c.birthdate is not null
                    and date_part('year', age(current_date, c.birthdate)) > 25
                group by
                    c.userid,
                    c.id,
                    c.driverslicencecountry,
                    c.birthdate
                having
                    sum(o.totalrun) > 200
            """
        )

    async def _get_org_members(self):
        rows = await DB_REPLICA.execute_query_get_data(
            query=f"""
                select customerdataid
                from customerdata__2__organization
                where organizationid = '{SPECIAL_CARS_ORG_ID}'
            """
        )
        rows = rows or []
        return {self._normalize_user_id(row["customerdataid"]) for row in rows}

    async def _get_org_member_count(self):
        rows = await DB_REPLICA.execute_query_get_data(
            query=f"""
                select count(*) as total
                from customerdata__2__organization
                where organizationid = '{SPECIAL_CARS_ORG_ID}'
            """
        )
        if not rows:
            return 0
        return int(rows[0]["total"])

    async def _log_assignment(self, user, api_response):
        birthdate = user["birthdate"]
        age = self._calc_age(birthdate) if isinstance(birthdate, date) else None
        await DB_TECH.execute_query_put_data_dynamic(
            table_name="integrations.a4_special_cars_log",
            data={
                "userid": str(user["userid"]),
                "driverslicencecountry": user["driverslicencecountry"],
                "birthdate": birthdate,
                "age_years": age,
                "totalrun_sum": user["totalrun_sum"],
                "assigned_org_id": SPECIAL_CARS_ORG_ID,
                "assigned_at": datetime.utcnow(),
                "api_response": str(api_response),
            },
        )

    async def main_worker(self):
        await initialize_db()
        logger.info("A4 special cars worker started.")

        candidates = await self._get_candidates()
        candidates = candidates or []
        logger.info("A4 candidates found: %s", len(candidates))

        org_members = await self._get_org_members()
        logger.info("A4 existing members: %s", len(org_members))
        to_assign = [
            user
            for user in candidates
            if self._normalize_user_id(user["id"]) not in org_members
        ]
        print(f"-------- to ass {len(to_assign)}")

        if not to_assign:
            logger.info("No users to assign A4 Special cars.")
            await shutdown_db()
            return

        logger.info("A4 users to assign after compare: %s", len(to_assign))

        async with ClientSession() as session:
            for i in range(0, len(to_assign), 100):
                chunk = to_assign[i : i + 100]
                chunk_user_ids = [str(user["userid"]) for user in chunk]
                response = await CT_MobilityClient().user_switch_org(
                    user_ids=chunk_user_ids,
                    organizations=[SPECIAL_CARS_ORG_ID],
                    http_session=session,
                )
                for user in chunk:
                    await self._log_assignment(user=user, api_response=response)

        total_members = await self._get_org_member_count()
        message = (
            "✅ Cron algorithm executed: A4 Special cars assigned to new users.\n"
            f"Assigned after compare: {len(to_assign)}\n"
            f"Total in organization: {total_members}"
        )
        await TG_BOT.send_message_to_tg(chat_id=CHAT_ID, message_text=message)

        logger.info("A4 special cars worker finished.")
        await shutdown_db()

