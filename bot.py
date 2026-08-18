import discord
import database
import importlib
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class RobloxInvitesBot(commands.Bot):
    def __init__(self, api, version, patch_notes):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        
        self.db = database.Database()
        self.api = api
        self.version = version
        self.patch_notes = patch_notes

    async def setup_hook(self):
        await self.api.start()
        await self.db.initalize()

        self.api.pool = self.db.pool

        self.metadata_manager = database.MetadataManager(self.db.pool)
        self.user_manager = database.UserManager(self.db.pool, self.api)
        self.presence_manager = database.PresenceManager(self.db.pool, self.api, self.user_manager)
        self.transfer_manager = database.TransferManager(self.db.pool)
        self.cgt_manager = database.CGTManager(self.db.pool, self.api)
        self.blacklist_manager = database.BlacklistManager(self.db.pool, self.api)
        self.settings_manager = database.SettingsManager(self.db.pool, self)
        self.stat_manager = database.StatManager(self.db.pool, self.api, self.user_manager)
        self.snapshot_manager = database.SnapshotManager(self.db.pool, self, self.api)
        self.leaderboard_manager = database.LeaderboardManager(self.db.pool, self, self.api)

        await self.load_extension("cogs.help_cog")
        await self.load_extension("cogs.user_cog")
        await self.load_extension("cogs.cgt_cog")
        await self.load_extension("cogs.blacklist_cog")
        await self.load_extension("cogs.settings_cog")
        await self.load_extension("cogs.persistent_cog")
        await self.load_extension("cogs.leaderboard_cog")
        await self.load_extension("cogs.server_cog")
        await self.load_extension("cogs.snapshot_cog")
        await self.load_extension("cogs.admin_cog")

        await self.tree.sync()

    async def reload_extensions(self, interaction):
        importlib.reload(database.users)
        importlib.reload(database.metadata)
        importlib.reload(database.transfers)
        importlib.reload(database.custom)
        importlib.reload(database.blacklist)
        importlib.reload(database.settings)
        importlib.reload(database.presences)
        importlib.reload(database.stats)
        importlib.reload(database.snapshots)
        importlib.reload(database.leaderboards)
        importlib.reload(database)

        self.metadata_manager = database.MetadataManager(self.db.pool)
        self.user_manager = database.UserManager(self.db.pool, self.api)
        self.presence_manager = database.PresenceManager(self.db.pool, self.api, self.user_manager)
        self.transfer_manager = database.TransferManager(self.db.pool)
        self.cgt_manager = database.CGTManager(self.db.pool, self.api)
        self.blacklist_manager = database.BlacklistManager(self.db.pool, self.api)
        self.settings_manager = database.SettingsManager(self.db.pool, self)
        self.stat_manager = database.StatManager(self.db.pool, self.api, self.user_manager)
        self.snapshot_manager = database.SnapshotManager(self.db.pool, self, self.api)
        self.leaderboard_manager = database.LeaderboardManager(self.db.pool, self, self.api)

        await self.reload_extension("cogs.help_cog")
        await self.reload_extension("cogs.user_cog")
        await self.reload_extension("cogs.cgt_cog")
        await self.reload_extension("cogs.blacklist_cog")
        await self.reload_extension("cogs.settings_cog")
        await self.reload_extension("cogs.leaderboard_cog")
        await self.reload_extension("cogs.persistent_cog")
        await self.reload_extension("cogs.server_cog")
        await self.reload_extension("cogs.snapshot_cog")
        await self.reload_extension("cogs.admin_cog")

        await interaction.followup.send("Successfully reloaded all extensions!")
        return True

    async def on_ready(self):
        for guild in self.guilds:
            await self.db.create_guild(guild)
        print(f"{self.user} is online and ready!")

    async def on_guild_join(self, guild):
        await self.db.create_guild(guild)

    async def on_member_remove(self, member):
        await self.user_manager.unlink_user(member, member.guild)