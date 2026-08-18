import database

class PresenceManager:
    def __init__(self, pool, api, user_manager):
        self.pool = pool
        self.api = api
        self.user_manager = user_manager
        self.queries = database.load_sql("presences.sql")

    async def save_presences(self, presence_type):
        user_ids = await self.user_manager.get_all_user_ids()
        p_keys = {
            "current": ["userId", "lastLocation", "placeId", "rootPlaceId", "gameId", "userPresenceType"],
            "old": ["user_id", "last_location", "place_id", "root_place_id", "game_instance_id", "user_status"]
        }
        if presence_type == "current":
            api_presences = await self.api.get_presences(user_ids)
            presences = api_presences["userPresences"]
        elif presence_type == "old":
            async with self.pool.acquire() as conn:
                presences = await conn.fetch(self.queries["get_all_presences"])

        presence_records = [
            (
                presence[p_keys[presence_type][0]],
                presence[p_keys[presence_type][1]],
                presence[p_keys[presence_type][2]],
                presence[p_keys[presence_type][3]],
                presence[p_keys[presence_type][4]],
                presence[p_keys[presence_type][5]]
            )
            for presence in presences
        ]

        async with self.pool.acquire() as conn:
            await conn.executemany(self.queries[f"save_{presence_type}_presences"], presence_records)

    async def erase_presence(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["erase_presence"], user_id, None, None, None, None, 0)

    async def get_presence(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(self.queries["get_presence"], user_id)

    async def get_guild_presences(self, guild, presence_type):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries[f"get_{presence_type}_guild_presences"], guild.id)
        
        if len(rows) > 0:
            presences = {
                row["user_id"]: row
                for row in rows
            }
        else:
            presences = {
                row["user_id"]: {
                    "last_location": None,
                    "place_id": None,
                    "root_place_id": None,
                    "game_instance_id": None,
                    "user_status": 0
                }
                for row in rows
            }

        return presences

    async def get_all_presences(self, presence_type):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_all_users"])
        
        user_ids = [row["user_id"] for row in rows]
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries[f"get_all_{presence_type}_presences"], user_ids)
        
        presences = {
            row["user_id"]: row
            for row in rows
        }

        return presences

    async def check_joins(self, guild, user_id, place_id, game_instance_id):
        joined = []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["check_joins"], place_id, game_instance_id, user_id)
            guild_users = await self.user_manager.get_guild_users(guild)
            joined_user_ids = [row["user_id"] for row in rows]

        for guild_user in guild_users:
            if guild_user["user_id"] in joined_user_ids:
                joined += [(guild_user["display_name"], guild_user["username"])]
        return joined
