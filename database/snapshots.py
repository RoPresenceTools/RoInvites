import database

class SnapshotManager:
    def __init__(self, pool, bot, api):
        self.pool = pool
        self.bot = bot
        self.api = api
        self.queries = database.load_sql("snapshots.sql")

    async def get_total_playtimes_unfiltered(self, user_ids):
        async with self.pool.acquire() as conn:
            total_rows = await conn.fetch(self.queries["get_total_playtimes_unfiltered"], user_ids)
            return total_rows

    async def get_game_playtimes_unfiltered(self, user_ids):
        async with self.pool.acquire() as conn:
            game_rows = await conn.fetch(self.queries["get_game_playtimes_unfiltered"], user_ids)
            return game_rows

    async def get_latest_snapshot_id(self, guild):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_latest_snapshot_id"], guild.id)

    async def save_snapshot(self, guild):
        user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            snapshot_id = await conn.fetchval(self.queries["save_snapshot_metadata"], guild.id)

        total_rows = await self.get_total_playtimes_unfiltered(user_ids)
        game_rows = await self.get_game_playtimes_unfiltered(user_ids)

        total_playtimes = [(snapshot_id, *row) for row in total_rows]
        game_playtimes = [(snapshot_id, *row) for row in game_rows]

        async with self.pool.acquire() as conn:
            await conn.executemany(self.queries["save_total_playtime_snapshot"], total_playtimes)
            await conn.executemany(self.queries["save_game_playtime_snapshot"], game_playtimes)

    async def remove_last_snapshot(self, guild):
        snapshot_id = await self.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["remove_last_snapshot"], guild.id, snapshot_id)
            return True
