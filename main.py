import asyncio
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from ct_api_integration import get_admin_session, user_orgs_switcher
from database import DB_REPLICA, DB_PROCEDURES
from app_config import NIGHT_WATCH_ORG, NIGHT_WATCH_EXTEND_ORG



async def remove_orgs_for_night():

    # get users and orgs
    sql_query = f"""SELECT 
    c.userid,
    co.organizationid 
FROM customerdata c
LEFT JOIN customerdata__2__organization co 
    ON c.id = co.customerdataid
WHERE c.isremoved = false
  AND c.isvalidatedbysecurity = true
  AND c.allowdrivewithoutbankcard = false
  AND EXTRACT(YEAR FROM AGE(c.birthdate)) >= 18 
  AND EXTRACT(YEAR FROM AGE(c.birthdate)) <= 24
  AND co.organizationid IN ('d41a9561-3d2d-40a1-99b1-b0ee013eaad3',
                             'f6477857-4eda-476c-bcf6-ae7500decd0f',
                             '01b1ddda-35b5-4360-a5c5-ad5e00746090',
                             '59d81c7d-e06f-479f-8562-ab4e00fba740')
  AND NOT EXISTS (
      SELECT 1
      FROM customerdata__2__organization co2
      WHERE co2.customerdataid = c.id
        AND co2.organizationid = '{NIGHT_WATCH_EXTEND_ORG}'
  )"""


    users_list = await DB_REPLICA.execute_query_get_data(query=sql_query)

    cyprus_time = datetime.now()
    r = await DB_PROCEDURES.save_user_organization_data(datetime_cyp=cyprus_time, data=users_list)
    print(r)

    a1 = []
    a2 = []
    a3 = []
    a4 = []

    for row in users_list:


        if str(row['organizationid']) == 'd41a9561-3d2d-40a1-99b1-b0ee013eaad3':
            a4.append(str(row['userid']))
        elif str(row['organizationid']) == 'f6477857-4eda-476c-bcf6-ae7500decd0f':
            a3.append(str(row['userid']))
        elif str(row['organizationid']) == '01b1ddda-35b5-4360-a5c5-ad5e00746090':
            a2.append(str(row['userid']))
        elif str(row['organizationid']) == '59d81c7d-e06f-479f-8562-ab4e00fba740':
            a1.append(str(row['userid']))

    s = await get_admin_session()


    r = await user_orgs_switcher(s, "d41a9561-3d2d-40a1-99b1-b0ee013eaad3", a4, assign=False)
    print(r)
    r = await user_orgs_switcher(s, "f6477857-4eda-476c-bcf6-ae7500decd0f", a3, assign=False)
    print(r)
    r = await user_orgs_switcher(s, "01b1ddda-35b5-4360-a5c5-ad5e00746090", a2, assign=False)
    print(r)
    r = await user_orgs_switcher(s, "59d81c7d-e06f-479f-8562-ab4e00fba740", a1, assign=False)
    print(r)


async def add_orgs_for_day():

    # get users and orgs
    sql_query = f"""SELECT user_id, org_id 
FROM night_watch_log
WHERE datetime_cyp >= (
    SELECT MAX(datetime_cyp)
    FROM night_watch_log
)
"""
    users_list = await DB_PROCEDURES.execute_query_get_data(query=sql_query)

    a1 = []
    a2 = []
    a3 = []
    a4 = []

    for row in users_list:

        if str(row['org_id']) == 'd41a9561-3d2d-40a1-99b1-b0ee013eaad3':
            a4.append(str(row['user_id']))
        elif str(row['org_id']) == 'f6477857-4eda-476c-bcf6-ae7500decd0f':
            a3.append(str(row['user_id']))
        elif str(row['org_id']) == '01b1ddda-35b5-4360-a5c5-ad5e00746090':
            a2.append(str(row['user_id']))
        elif str(row['org_id']) == '59d81c7d-e06f-479f-8562-ab4e00fba740':
            a1.append(str(row['user_id']))

    s = await get_admin_session()


    r = await user_orgs_switcher(s, "d41a9561-3d2d-40a1-99b1-b0ee013eaad3", a4, assign=True)
    print(r)
    r = await user_orgs_switcher(s, "f6477857-4eda-476c-bcf6-ae7500decd0f", a3, assign=True)
    print(r)
    r = await user_orgs_switcher(s, "01b1ddda-35b5-4360-a5c5-ad5e00746090", a2, assign=True)
    print(r)
    r = await user_orgs_switcher(s, "59d81c7d-e06f-479f-8562-ab4e00fba740", a1, assign=True)
    print(r)


async def add_orgs_night_watch():
    sql_query = f"""SELECT 
        c.userid
    FROM customerdata c
    left join customerdata__2__organization co on c.id  = co.customerdataid 
    where c.isremoved = false 
    and c.isvalidatedbysecurity = true 
    and c.allowdrivewithoutbankcard = false
    and EXTRACT(YEAR FROM AGE(c.birthdate)) >= 18 and EXTRACT(YEAR FROM AGE(c.birthdate)) <= 24 
    and co.organizationid not in ('{NIGHT_WATCH_EXTEND_ORG}')"""

    users_list = await DB_REPLICA.execute_query_get_data(query=sql_query)
    users_list = [str(user['userid']) for user in users_list]

    s = await get_admin_session()
    r = await user_orgs_switcher(s, NIGHT_WATCH_ORG, users_list, assign=True)
    print(r)

async def remove_orgs_night_watch():
    sql_query = f"""SELECT 
    c.userid,
    co.organizationid 
FROM customerdata c
left join customerdata__2__organization co on c.id  = co.customerdataid 
where c.isremoved = false 
and c.isvalidatedbysecurity = true 
and c.allowdrivewithoutbankcard = false
and EXTRACT(YEAR FROM AGE(c.birthdate)) >= 18 and EXTRACT(YEAR FROM AGE(c.birthdate)) <= 24 
and co.organizationid in ('{NIGHT_WATCH_ORG}')"""

    users_list = await DB_REPLICA.execute_query_get_data(query=sql_query)
    users_list = [str(user['userid']) for user in users_list]

    s = await get_admin_session()
    r = await user_orgs_switcher(s, NIGHT_WATCH_ORG, users_list, assign=False)
    print(r)


def night():
    asyncio.run(add_orgs_night_watch())
    asyncio.run(remove_orgs_for_night())


def day():
    asyncio.run(add_orgs_for_day())
    asyncio.run(remove_orgs_night_watch())


def main():

    print("ORG switcher started...")

    script_timezone = pytz.timezone('Asia/Nicosia')
    scheduler = BlockingScheduler(timezone=script_timezone)

    scheduler.add_job(day, 'cron', misfire_grace_time=120, hour='6', minute='0')
    scheduler.add_job(night, 'cron', misfire_grace_time=120, hour='21', minute='0')
    scheduler.start()

# Запуск основного цикла
if __name__ == "__main__":
    main()



