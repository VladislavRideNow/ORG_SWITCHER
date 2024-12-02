import json
import aiohttp
import base64

from app_config import MAIN_HOST, ADMIN_AUTH

async def get_admin_session():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{MAIN_HOST}/api/') as response:
            sessid = response.cookies.get('sessid').value
            url_log = f"{MAIN_HOST}/admin/login?sessid={sessid}"
            async with session.post(url_log, data=json.dumps(ADMIN_AUTH)) as login_response:
                await login_response.text()
                return sessid


async def user_orgs_switcher(sessid, org_id, user_ids, assign):
    url = f"{MAIN_HOST}/admin/organization/massAssign/{org_id}?sessid={sessid}"

    # Преобразуем список user_ids в строку и кодируем в base64
    user_ids_str = "\n".join(user_ids)  # Преобразуем список в строку
    encoded_file = base64.b64encode(user_ids_str.encode('utf-8')).decode('utf-8')

    # Формируем строку с base64-данными
    file_content = f"data:text/plain;base64,{encoded_file}"

    data = {
        "AssignmentMode": 7,  # 5 - User phone, 6 - User email, 7 - User ID, 8 - all users
        "File": file_content,  # Закодированный файл в base64
        "Assign": assign  # true - assign, false - unassign
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                print("Request was successful.")
                result = await response.json()
                print(result)
            else:
                print(f"Request failed with status: {response.status}")
                error = await response.text()
                print(error)



