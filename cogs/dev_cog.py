import discord
import getpass
import logging
from discord import app_commands
from discord.ext import commands
from pathlib import Path
from subprocess import Popen
from datetime import datetime

logger = logging.getLogger(__name__)

class DevCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    dev = app_commands.Group(
        name="dev",
        description="Developer commands",
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

    @dev.command(name="reload", description="Reloads all extensions")
    async def admin_reload_extensions(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.reload_extensions(interaction)
        if success != True:
            await interaction.followup.send(f"Couldn't reload extensions.")

    @dev.command(name="backup", description="Creates a .sql server backup")
    async def create_backup(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        filename = datetime.now().strftime("backup_%m-%d-%Y_%H-%M-%S.sql")
        backup_proc = Popen(["pg_dump", "-U", getpass.getuser(), "-d", "roblox_invites", "-f", f"./database/backups/{filename}"])
        exit_code = backup_proc.wait()
        if exit_code == 0:
            logger.info(f"Created a server backup")
            await interaction.followup.send("Successfully created a backup!")
        else:
            await interaction.followup.send(f"Couldn't create a backup. Exit code: {exit_code}")

    @dev.command(name="update_message", description="Shows the current update message")
    async def send_update_message(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)
            return

        patch_notes = Path(__file__).parent / ".." / "patch_notes.txt"
        if patch_notes.exists():
            embed = discord.Embed(
                title="An update has been issued!",
                description=patch_notes.read_text().format(self.bot.version, self.bot.version),
                color=discord.Color.blue()
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @dev.command(name="add_admin", description="Gives admin to a user")
    async def add_admin(
        self, 
        interaction: discord.Interaction,
        user: discord.User
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)
            return

        await self.bot.user_manager.add_admin(user)
        await interaction.response.send_message("Successfully added admin to this user!", ephemeral=True)

    @dev.command(name="remove_admin", description="Removes admin from a user")
    async def remove_admin(
        self, 
        interaction: discord.Interaction,
        user: discord.User
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)
            return

        await self.bot.user_manager.remove_admin(user)
        await interaction.response.send_message("Successfully removed admin from this user!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DevCog(bot))
