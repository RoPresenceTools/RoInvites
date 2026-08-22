import asyncpg
from pathlib import Path

class Database:
    def __init__(self):
        self.pool = None
        self.pg_user = Path("/run/secrets/pg_user").read_text().strip()
        self.pg_pwd = Path("/run/secrets/pg_pw").read_text()

    async def initalize(self):
        await self.connect()
        await self.create_tables()
        await self.apply_migrations()

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=self.pg_user,
            password=self.pg_pwd,
            database="roblox_invites",
            host="postgres"
        )
    
    async def create_tables(self):
        schema_path = Path(__file__).parent / "schema.sql"
        async with self.pool.acquire() as conn:
            await conn.execute(schema_path.read_text())

    async def apply_migrations(self):
        migration_path = Path(__file__).parent / "migrations"
        async with self.pool.acquire() as conn:
            for migration_sql in migration_path.glob("*.sql"):
                await conn.execute(migration_sql.read_text())

    async def create_guild(self, guild):
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO guild_settings (guild_id)
                VALUES ($1)
                ON CONFLICT (guild_id)
                DO NOTHING
            """, guild.id)
