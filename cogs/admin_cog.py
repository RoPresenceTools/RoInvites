import discord
import getpass
import logging
from discord import app_commands
from discord.ext import commands
from pathlib import Path
from subprocess import Popen
from datetime import datetime

logger = logging.getLogger(__name__)

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def user_autocomplete(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> list[app_commands.Choice[str]]:
        users = await interaction.client.user_manager.get_all_users()
        return [
            app_commands.Choice(name=data["username"], value=user_id)
            for user_id, data in users.items()
            if query.lower() in data["username"].lower()
        ]

    admin = app_commands.Group(
        name="admin",
        description="Admin commands",
        allowed_installs=app_commands.AppInstallationType(
            guild=True,
            user=True
        ),
        allowed_contexts=app_commands.AppCommandContext(
            guild=True,
            dm_channel=True,
            private_channel=True
        )
    )

    @admin.command(name="reload", description="Reloads all extensions")
    async def admin_reload_extensions(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.reload_extensions(interaction)
        if success != True:
            await interaction.followup.send(f"Couldn't reload extensions.")

    @admin.command(name="remove", description="Removes a user from RoInvites")
    @app_commands.autocomplete(user_id=user_autocomplete)
    async def admin_remove_user(
        self, 
        interaction: discord.Interaction,
        user_id: int
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.user_manager.remove_user_id(user_id)
        if success == True:
            logger.info(f"Removed user with ID {user_id} from RoInvites")
            await interaction.followup.send(f"Removed this user from RoInvites.")
        else:
            await interaction.followup.send(f"This user isn't associated with RoInvites.")

    @admin.command(name="backup", description="Creates a .sql server backup")
    async def create_backup(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        filename = datetime.now().strftime("backup_%m-%d-%Y_%H-%M-%S.sql")
        backup_proc = Popen(["pg_dump", "-U", getpass.getuser(), "-d", "roblox_invites", "-f", f"./database/backups/{filename}"])
        exit_code = backup_proc.wait()
        if exit_code == 0:
            logger.info(f"Created a server backup")
            await interaction.followup.send("Successfully created a backup!")
        else:
            await interaction.followup.send(f"Couldn't create a backup. Exit code: {exit_code}")

    @admin.command(name="announce", description="Sends a global announcement")
    async def send_announcement(
        self, 
        interaction: discord.Interaction,
        announcement_text: str
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        for guild in self.bot.guilds:
            announcement_channel = await self.bot.settings_manager.get_channel(guild, "announcement")

            embed = discord.Embed(
                title="Global Announcement",
                description=announcement_text.replace("\\n", "\n"),
                color=discord.Color.dark_purple()
            )

            user_id = await self.bot.user_manager.get_user_from_discord_id(interaction.user)
            if user_id is not None:
                username = await self.bot.user_manager.get_username(user_id)
                display_name = await self.bot.user_manager.get_display_name(user_id)
                if not None in (username, display_name):
                    embed.title = f"Announcement from {display_name}"
                thumbnail_url = await self.bot.api.get_avatar_headshot(user_id)
                if thumbnail_url is not None:
                    embed.set_thumbnail(url=thumbnail_url)

            try:
                channel = self.bot.get_channel(announcement_channel)
                await channel.send(embed=embed)
            except:
                pass
        logger.info(f"Sent global announcement: {announcement_text[:20]}...")
        await interaction.followup.send("Successfully sent announcement!")

    @admin.command(name="update_message", description="Shows the current update message")
    async def send_update_message(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)

        patch_notes = Path(__file__).parent / ".." / "patch_notes.txt"
        if patch_notes.exists():
            embed = discord.Embed(
                title="An update has been issued!",
                description=patch_notes.read_text().format(self.bot.version, self.bot.version),
                color=discord.Color.blue()
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
