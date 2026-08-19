from .load_sql import load_sql

class MetadataManager:
    def __init__(self, pool):
        self.pool = pool
        self.queries = load_sql("metadata.sql")

    async def get_version(self):
        async with self.pool.acquire() as conn:
            saved_version = await conn.fetchval(self.queries["get_version"])

            if saved_version is None:
                return "0.0.0"
            else:
                return saved_version

    async def set_version(self, version_string):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["set_version"], version_string)
