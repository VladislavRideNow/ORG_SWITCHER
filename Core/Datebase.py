import asyncpg
import setting as cfg


class DatabasePG:
    def __init__(self, user, password, host, port, database, min_conn=1, max_conn=100):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.max_retries = 5
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.pool = None

    async def init_pool(self):
        """ Инициализация пула соединений """
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                min_size=self.min_conn,
                max_size=self.max_conn,
                timeout=10  # Таймаут подключения
            )
            print(f"✅ Пул соединений создан для {self.database}")
        except asyncpg.PostgresError as e:
            print(f"❌ Ошибка создания пула соединений: {e}")

    async def close_pool(self):
        """ Закрытие пула соединений """
        if self.pool:
            await self.pool.close()
            print(f"🔴 Пул соединений {self.database} закрыт")

    async def execute_query_get_data(self, query):
        """ Выполняет SELECT-запрос и возвращает данные """
        if not self.pool:
            return {"error": "Пул соединений не инициализирован"}

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    rows = await connection.fetch(query)
                    return [dict(row) for row in rows] if rows else None
        except asyncpg.PostgresError as e:
            print(f"🚨 Ошибка Postgres: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"❗ Неожиданная ошибка: {e}")
            return {"error": str(e)}

    async def execute_query_put_data(self, query):
        """ Выполняет INSERT/UPDATE/DELETE-запрос """
        if not self.pool:
            return {"error": "Пул соединений не инициализирован"}

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(query)
                    return {"status": 200, "message": "Операция выполнена успешно"}
        except asyncpg.PostgresError as e:
            print(f"🚨 Ошибка Postgres: {e}")
            return {"error": str(e)}

    async def execute_query_put_data_dynamic(self, table_name: str, data: dict):
        """ Динамический INSERT """
        if not self.pool:
            return {"error": "Пул соединений не инициализирован"}

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(f"${i + 1}" for i in range(len(data)))
                    values = tuple(data.values())

                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    await connection.execute(query, *values)
                    return {"status": 200, "message": "Data inserted successfully"}
        except asyncpg.PostgresError as e:
            print(f"🚨 Error Postgres: {e}")
            return {"error": str(e)}

    async def execute_query_update_data_dynamic(self, table_name: str, data: dict, search_field: str,
                                                search_value: any):
        """ Updates data dynamically using the connection pool """
        if not self.pool:
            return {"error": "Connection pool is not initialized"}

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    update_parts = ', '.join(f"{key} = ${i + 1}" for i, key in enumerate(data.keys()))
                    last_index = len(data) + 1
                    values = list(data.values()) + [search_value]

                    query = f"UPDATE {table_name} SET {update_parts} WHERE {search_field} = ${last_index}"
                    await connection.execute(query, *values)

                    return {"status": 200, "message": "Data updated successfully"}
        except asyncpg.PostgresError as e:
            print(f"🚨 PostgreSQL error: {e}")
            return {"status": 500, "message": str(e)}


# Create database connection instances
DB_REPLICA = DatabasePG(cfg.REPL_USER, cfg.REPL_PASS, cfg.REPL_HOST, cfg.REPL_PORT, cfg.REPL_DB)
DB_TECH = DatabasePG(cfg.TECH_USER, cfg.TECH_PASS, cfg.TECH_HOST, cfg.TECH_PORT, cfg.TECH_DB)

async def initialize_db():
    """Init connection pools for all databases."""
    await DB_REPLICA.init_pool()
    await DB_TECH.init_pool()


async def shutdown_db():
    """Close connection pools for all databases."""
    await DB_REPLICA.close_pool()
    await DB_TECH.close_pool()
