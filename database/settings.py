from .load_sql import load_sql

class SettingsManager:
    def __init__(self, pool, bot):
        self.bot = bot
        self.pool = pool
        self.queries = load_sql("settings.sql")

    async def get_channel(self, guild, channel_type):
        async with self.pool.acquire() as conn:
            channel = await conn.fetchval(self.queries[f"get_{channel_type}_channel"], guild.id)
        return channel

    async def set_channel(self, guild, channel_type, channel):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries[f"set_{channel_type}_channel"], guild.id, channel.id)

        await channel.send(f"The {channel_type} channel has been set to this channel.")
        return True
