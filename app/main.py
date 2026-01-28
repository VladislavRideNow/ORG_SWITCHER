import asyncio

import pytz
from aiohttp import ClientSession
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.adapters.tg_bot import TG_BOT
from app.adapters.ct_mobility_client import CT_MobilityClient
from app.core.database import initialize_db, shutdown_db, DB_REPLICA, DB_TECH

WAITING_FOR_PAYMENT_CONFIG = {
    "driver license countries": ["IND"],
    "org_id": ["ffd9b099-daf9-46b7-8c71-ad2200abec28"],
    "age_limit": 100,
}

BAD_DEBTOR_CONFIG = {
    "driver license countries": ["IND"],
    "org_id": ["f6477857-4eda-476c-bcf6-ae7500decd0f"],
    "age_limit": 21,
}

CHAT_ID = -954331597
#CHAT_ID = 368038740


async def check_user_in_log(user_id: str):
    query = f"""select * from integrations.orgswitcher_log 
where userid = '{user_id}'
"""
    rows = await DB_TECH.execute_query_get_data(query)
    print(f"Check log for user {user_id}, found rows: {rows}")
    if rows is None:
        return False
    else:
        return True


async def main_worker():
    """
    Main entry point for ETL worker (for debugging/manual run)
    """

    # INIT DATABASES POOLS
    await initialize_db()

    # YOUR WORKER LOGIC HERE 🇮🇳
    print("Worker is running...")

    # WAITING FOR PAYMENT FLOW
    users_by_driver_license_countries = await DB_REPLICA.execute_query_get_data(
        query=f"""
            select userid, displayname, c.driverslicencecountry, DATE_PART('year', AGE(c.birthdate)) AS age from customerdata c 
            where c.driverslicencecountry in ({', '.join(f"'{country}'" for country in WAITING_FOR_PAYMENT_CONFIG['driver license countries'])}) 
            and c.birthdate is not null and (creationdatetime >= now() - interval '3 days')
        """
    )

    if users_by_driver_license_countries is None:
        users_by_driver_license_countries = []
    else:
        for user in users_by_driver_license_countries:
            userid = str(user["userid"])
            user_in_log = await check_user_in_log(user_id=userid)

            user_link = f"https://ridenow3.ct.ms/Content/admin/index.html#/modal/customer?id={userid}"
            if not user_in_log and user["age"] <= WAITING_FOR_PAYMENT_CONFIG['age_limit']:

                # Change user's organization assignment logic here if needed
                async with ClientSession() as session:
                    r = await CT_MobilityClient().user_switch_org(user_ids=[userid],
                                                                  organizations=WAITING_FOR_PAYMENT_CONFIG['org_id'],
                                                                  http_session=session)

                insert_result = await DB_TECH.execute_query_put_data_dynamic(
                    table_name="integrations.orgswitcher_log",
                    data={
                        "userid": userid,
                        "datetime": datetime.now(),
                        "assigned_organizations": f"Driver license country requires waiting for payment, assigned orgs Waiting for payment: {WAITING_FOR_PAYMENT_CONFIG['org_id']}",
                        "api_response": str(r),
                    }
                )
                print(f"Inserted log for user {userid}: {insert_result}")

                # Send Telegram notification
                message = (
                    f"""🔥 <b>New User Alert!</b>  
    👤 <a href="{user_link}">{user['displayname']}</a>  
    🕓 Status set: <b>Waiting for Payment</b>  
    🌍 Driver License Country: <b>{user["driverslicencecountry"]}</b>  
    🎂 Age: <b>{round(user['age'])}</b> years 
    ⚙️ Org assignment pending due to license country."""
                )
                await TG_BOT.send_message_to_tg(
                    chat_id=CHAT_ID,
                    message_text=message,
                )
                print(f"Sent Telegram notification for user {userid}.")
            else:
                print(f"User {userid} already in log, skipping.")

    # BAD DEBTOR FLOW
    users_by_driver_license_countries = await DB_REPLICA.execute_query_get_data(
        query=f"""
            select userid, displayname, c.driverslicencecountry, DATE_PART('year', AGE(c.birthdate)) AS age from customerdata c 
            where c.driverslicencecountry not in ({', '.join(f"'{country}'" for country in BAD_DEBTOR_CONFIG['driver license countries'])}) 
            and c.birthdate is not null and (creationdatetime >= now() - interval '3 days')
        """
    )
    for user in users_by_driver_license_countries:
        userid = str(user["userid"])
        user_in_log = await check_user_in_log(user_id=userid)

        user_link = f"https://ridenow3.ct.ms/Content/admin/index.html#/modal/customer?id={userid}"
        if not user_in_log and user["age"] <= BAD_DEBTOR_CONFIG['age_limit']:

            # Change user's organization assignment logic here if needed
            async with ClientSession() as session:
                r = await CT_MobilityClient().user_switch_org(user_ids=[userid],
                                                              organizations=BAD_DEBTOR_CONFIG['org_id'],
                                                              http_session=session)

            insert_result = await DB_TECH.execute_query_put_data_dynamic(
                table_name="integrations.orgswitcher_log",
                data={
                    "userid": user["userid"],
                    "datetime": datetime.now(),
                    "assigned_organizations": f"Client age requires bad debtor orgs: {BAD_DEBTOR_CONFIG['org_id']}",
                    "api_response": str(r),
                }
            )
            print(f"Inserted log for user {user['userid']}: {insert_result}")

            # Send Telegram notification
            message = (
                f"""🔥 <b>New User Alert!</b>
👤 <a href="{user_link}">{user['displayname']}</a>
🕓 Status set: <b>Bad Debtor</b>
🌍 Driver License Country: <b>{user["driverslicencecountry"]}</b>
🎂 Age: <b>{round(user['age'])}</b> years
⚙️ Org assignment pending due to age criteria."""
            )
            await TG_BOT.send_message_to_tg(
                chat_id=CHAT_ID,
                message_text=message,
            )
            print(f"Sent Telegram notification for user {user['userid']}.")

    # SHUTDOWN DATABASES POOLS
    await shutdown_db()


def main():
    print("ORG switcher started...")

    script_timezone = pytz.timezone('Asia/Nicosia')
    scheduler = AsyncIOScheduler(timezone=script_timezone)

    # Schedule async job every 2 minutes
    scheduler.add_job(main_worker, 'interval', minutes=2)

    scheduler.start()

    # Keep the event loop running
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    #asyncio.run(main_worker())
    main()
