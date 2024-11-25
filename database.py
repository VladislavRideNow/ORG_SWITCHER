import json
import asyncpg
import app_config as cfg

class DatabasePG:
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def __str__(self):
        return f'{self.database}'

    async def _get_connection(self):
        try:
            connection = await asyncpg.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            #print(f"Successfully connected to Postgres SQL {self.database} database as {self.user} user")
            return connection
        except (Exception, asyncpg.PostgresError) as error:
            print("Connection error", error)
            return None

    async def execute_query_get_data(self, query):
        connection = await self._get_connection()
        if connection is None:
            return {"error": "Could not establish connection"}
        try:
            async with connection.transaction():
                rows = await connection.fetch(query)
                if rows:
                    return [dict(row) for row in rows]
                else:
                    return None
        except asyncpg.PostgresError as e:
            print(f"Postgres error: {e}")
            return {"error": f"An error occurred: {e}"}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": f"An unexpected error occurred: {e}"}
        finally:
            await connection.close()

    async def execute_query_get_data_json(self, query):
        connection = await self._get_connection()
        if connection is None:
            return {"error": "Could not establish connection"}
        try:
            async with connection.transaction():
                rows = await connection.fetch(query)
                if rows:
                    result = str([dict(row) for row in rows])
                    return json.dumps(result, indent=4, default=str)
                else:
                    return json.dumps([], indent=4, default=str)  # Return an empty JSON list
        except asyncpg.PostgresError as e:
            print(f"Postgres error: {e}")
            return {"error": f"An error occurred: {e}"}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": f"An unexpected error occurred: {e}"}
        finally:
            await connection.close()

    async def execute_query_put_data(self, query):
        connection = await self._get_connection()
        if connection is None:
            return {"error": "Could not establish connection"}
        try:
            async with connection.transaction():
                await connection.execute(query)
                return {"status": 200, "message": "Data inserted successfully"}
        except asyncpg.PostgresError as e:
            print(f"Postgres error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            await connection.close()

    async def execute_query_put_data_dynamic(self, table_name: str, data: dict[str, any]):
        connection = await self._get_connection()
        if connection is None:
            return {"error": "Could not establish connection"}
        try:
            async with connection.transaction():
                columns = ', '.join(data.keys())
                placeholders = ', '.join(f"${i + 1}" for i in range(len(data)))
                values = tuple(data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                await connection.execute(query, *values)
                return {"status": 200, "message": "Data inserted successfully"}
        except asyncpg.PostgresError as e:
            return {"Postgres error": f"{e}"}
        except Exception as e:
            return {"Unexpected error": f"{e}"}
        finally:
            await connection.close()

    async def execute_query_update_data_dynamic(self, table_name: str, data: dict[str, any], search_field: str,
                                                search_value: any):
        connection = await self._get_connection()
        if connection is None:
            return {"error": "Could not establish connection"}
        try:
            async with connection.transaction():
                update_parts = ', '.join(f"{key} = ${i + 1}" for i, key in enumerate(data.keys()))
                last_index = len(data) + 1
                values = list(data.values()) + [search_value]
                query = f"UPDATE {table_name} SET {update_parts} WHERE {search_field} = ${last_index}"
                await connection.execute(query, *values)
                return {"status": 200, "message": "Data updated successfully"}
        except asyncpg.PostgresError as e:
            return {"status": 500, "message": f"{e}"}
        finally:
            await connection.close()

    async def save_user_organization_data(self, datetime_cyp, data: list[dict[str, any]]):
        connection = await self._get_connection()
        if connection is None:
            return {"error": "Could not establish connection"}

        try:
            async with connection.transaction():
                # Запрос для вставки данных
                query = '''
                INSERT INTO night_watch_log (datetime_cyp, user_id, org_id)
                VALUES ($1, $2, $3)
                '''

                # Процесс вставки всех записей
                for record in data:
                    await connection.execute(query, datetime_cyp, record['userid'], record['organizationid'])

                return {"status": 200, "message": "Data inserted successfully"}
        except asyncpg.PostgresError as e:
            return {"status": 500, "message": f"{e}"}
        finally:
            await connection.close()


# Instantiate Database objects
DB_REPLICA = DatabasePG(user=cfg.REPL_USER, password=cfg.REPL_PASS, host=cfg.REPL_HOST, port=cfg.REPL_PORT,
                        database=cfg.REPL_DB)
DB_PROCEDURES = DatabasePG(user=cfg.PROC_USER, password=cfg.PROC_PASS, host=cfg.PROC_HOST, port=cfg.PROC_PORT,
                           database=cfg.PROC_DB)
