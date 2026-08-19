from .load_sql import load_sql

class BlacklistManager:
    def __init__(self, pool, api):
        self.pool = pool
        self.api = api
        self.queries = load_sql("blacklist.sql")

    async def check_blacklist(self, guild, place_id):
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval(self.queries["check_blacklist"], guild.id, place_id)
            return exists

    async def add_blacklist(self, guild, place_id, game_name):
        if not await self.check_blacklist(guild, place_id):
            async with self.pool.acquire() as conn:
                await conn.execute(self.queries["add_blacklist"], guild.id, place_id, game_name)
            return True
        else:
            return False

    async def remove_blacklist(self, guild, place_id):
        if await self.check_blacklist(guild, place_id):
            async with self.pool.acquire() as conn:
                await conn.execute(self.queries["remove_blacklist"], guild.id, place_id)
            return True
        else:
            return False

    async def get_blacklisted_games(self, guild, query):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_blacklisted_games"], guild.id, query)
            return rows
