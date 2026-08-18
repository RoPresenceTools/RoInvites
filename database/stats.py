import database
from datetime import datetime

class StatManager:
    def __init__(self, pool, api, user_manager):
        self.pool = pool
        self.api = api
        self.user_manager = user_manager
        self.queries = database.load_sql("stats.sql")
        
    async def check_currently_playing(self, user_id):
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval(self.queries["check_currently_playing"], user_id)
            return exists

    async def check_if_game_played(self, guild, place_id):
        guild_user_ids = await self.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval(self.queries["check_if_game_played"], guild_user_ids, place_id)
            return exists

    async def get_current_place_id(self, user_id):
        async with self.pool.acquire() as conn:
            place_id = await conn.fetchval(self.queries["get_current_place_id"], user_id)
            if place_id is None:
                return 0
            return place_id

    async def get_total_playtime(self, user_id):
        async with self.pool.acquire() as conn:
            total_playtime = await conn.fetchval(self.queries["get_total_playtime"], user_id)
            if total_playtime is None:
                return 0
            return round(total_playtime)

    async def get_total_game_playtime(self, place_id):
        async with self.pool.acquire() as conn:
            playtime = await conn.fetchval(self.queries["get_total_game_playtime"], place_id)
            if playtime is None:
                return 0
            return round(playtime)

    async def get_game_playtime(self, user_id, place_id):
        async with self.pool.acquire() as conn:
            playtime = await conn.fetchval(self.queries["get_game_playtime"], user_id, place_id)
            if playtime is None:
                return 0
            return round(playtime)

    async def get_current_playtime(self, user_id):
        async with self.pool.acquire() as conn:
            start_time = await conn.fetchval(self.queries["get_current_playtime"], user_id)
            if start_time is None:
                return 0
            diff = datetime.now() - start_time
            current_playtime = round(diff.total_seconds())
            return round(current_playtime)

    async def get_current_playtime_placeid(self, user_id, root_place_id):
        async with self.pool.acquire() as conn:
            start_time = await conn.fetchval(self.queries["get_current_playtime_placeid"], user_id, root_place_id)
            if start_time is None:
                return 0
            diff = datetime.now() - start_time
            current_playtime = round(diff.total_seconds())
            return round(current_playtime)

    async def get_current_playtimes(self, user_ids):
        async with self.pool.acquire() as conn:
            current_rows = await conn.fetch(self.queries["get_current_playtimes"], user_ids)
            return current_rows

    async def update_game_playtime(self, user_id, place_id, playtime):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["update_game_playtime"], user_id, place_id, playtime)

    async def update_total_playtime(self, user_id):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_static_total_userid"], user_id)
            total_playtime = sum(row["playtime"] for row in rows)

            await conn.execute(self.queries["update_total_playtime"], user_id, total_playtime)

    async def set_currently_playing(self, user_id, place_id):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["set_currently_playing"], user_id, place_id)

    async def remove_currently_playing(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["remove_currently_playing"], user_id)

    async def get_playtime_str(self, user_id=None, place_id=None, playtime_type=None, playtime=0):
        if playtime == 0 and not None in (user_id, place_id, playtime_type):
            root_place_id = await self.api.get_root_place_id(place_id)
            if playtime_type == "both":
                playtime += await self.get_game_playtime(user_id, root_place_id)
            if playtime_type in ["current", "both"]:
                playtime += await self.get_current_playtime_placeid(user_id, root_place_id)

        hours = round(playtime // 3600)
        minutes = round((playtime % 3600) // 60)
        seconds = round(playtime % 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    async def start_tracking_playtime(self, user_id, place_id):
        if await self.check_currently_playing(user_id):
            await self.finish_tracking_playtime(user_id)
        root_place_id = await self.api.get_root_place_id(place_id)
        await self.set_currently_playing(user_id, root_place_id)

    async def finish_tracking_playtime(self, user_id):
        if await self.check_currently_playing(user_id):
            current = await self.get_current_playtime(user_id)
            root_place_id = await self.get_current_place_id(user_id)
            await self.update_game_playtime(user_id, root_place_id, current)
            await self.update_total_playtime(user_id)
            await self.remove_currently_playing(user_id)
