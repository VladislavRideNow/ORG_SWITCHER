from ct_api_integration import user_orgs_switcher, get_admin_session
from database import DB_REPLICA


async def bad_debtor_add():
    # get users and orgs
    sql_query = f"""select c.userid from customerdata c 
where driverslicencecountry like '%IND%' and creationdatetime >= CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - interval '30 minutes'"""
    users_list = await DB_REPLICA.execute_query_get_data(query=sql_query)

    users = []

    for user in users_list:
        users.append(str(user['userid']))

    if len(users) == 0:
        print("No new Indians clients added to Bad Debtor org")
    else:
        print(f"New Indians clients added to Bad Debtor org. Count: {len(users)}")
        s = await get_admin_session()
        r = await user_orgs_switcher(s, "f6477857-4eda-476c-bcf6-ae7500decd0f", users, assign=False)
        print(r)



