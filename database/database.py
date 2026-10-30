import asyncpg
import getpass
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
        self.pg_user = getpass.getuser()
        self.pg_pwd = ""

    async def initalize(self):
        await self.connect()
        await self.create_tables()
        await self.apply_migrations()
        logger.info("Initialized database")

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.pg_user,
                password=self.pg_pwd,
                database="roblox_invites",
                host="localhost"
            )
        except Exception:
            logger.critical("Failed to connect to the database", exc_info=True)
            sys.exit(1)
    
    async def create_tables(self):
        try:
            schema_path = Path(__file__).parent / "sql" / "schema.sql"
            async with self.pool.acquire() as conn:
                await conn.execute(schema_path.read_text())
        except Exception:
            logger.critical("Failed to apply the schema to the roblox_invites database", exc_info=True)
            sys.exit(1)

    async def apply_migrations(self):
        try:
            migration_path = Path(__file__).parent / "migrations"
            async with self.pool.acquire() as conn:
                for migration_sql in migration_path.glob("*.sql"):
                    await conn.execute(migration_sql.read_text())
        except Exception:
            logger.critical("Failed to apply database migrations", exc_info=True)
            sys.exit(1)

    async def create_guild(self, guild):
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO guild_settings (guild_id)
                VALUES ($1)
                ON CONFLICT (guild_id)
                DO NOTHING
            """, guild.id)
