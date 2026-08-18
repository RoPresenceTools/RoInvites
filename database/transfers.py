from .load_sql import load_sql

class TransferManager:
    def __init__(self, pool):
        self.pool = pool
        self.queries = load_sql("transfers.sql")

    async def get_transfer(self, user_id):
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(self.queries["get_transfer"], user_id)
            return row
        except:
            return {}
    
    async def check_transfer(self, user_id):
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval(self.queries["check_transfer"], user_id)
            return exists

    async def add_transfer(self, user_id, old_place_id, old_game_instance_id):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["add_transfer"], user_id, old_game_instance_id, old_place_id)
            return True

    async def remove_transfer(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["remove_transfer"], user_id)
            return True