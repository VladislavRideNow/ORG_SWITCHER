from ct_api_integration import user_orgs_switcher, get_admin_session
from database import DB_REPLICA


async def bad_debtor_add():
    # get users and orgs
    sql_query = f"""select c.userid from customerdata c 
where driverslicencecountry like '%IND%' and creationdatetime >= CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - interval '3 day'"""
    users_list = await DB_REPLICA.execute_query_get_data(query=sql_query)

    users = []

    if len(users_list) == 0:
        print("No new Indians clients added to Bad Debtor org")
    else:
        for user in users_list:
            users.append(str(user['userid']))

        print(f"New Indians clients added to Bad Debtor org. Count: {len(users)}")
        s = await get_admin_session()
        r = await user_orgs_switcher(s, "d41a9561-3d2d-40a1-99b1-b0ee013eaad3", users, assign=False)
        print(r)
        r = await user_orgs_switcher(s, "f6477857-4eda-476c-bcf6-ae7500decd0f", users, assign=True)
        print(r)
        r = await user_orgs_switcher(s, "01b1ddda-35b5-4360-a5c5-ad5e00746090", users, assign=False)
        print(r)
        r = await user_orgs_switcher(s, "59d81c7d-e06f-479f-8562-ab4e00fba740", users, assign=False)
        print(r)
        r = await user_orgs_switcher(s, "71a44ddf-4085-48c9-8516-adea00bb9f46", users, assign=False)
        print(r)




