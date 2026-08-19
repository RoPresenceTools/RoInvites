import discord
import getpass
from discord import app_commands
from discord.ext import commands
from subprocess import Popen
from datetime import datetime

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

            try:
                channel = self.bot.get_channel(announcement_channel)
                await channel.send(embed=embed)
            except:
                pass
        await interaction.followup.send("Successfully sent announcement!")

    @admin.command(name="update_message", description="Shows the current update message")
    async def send_update_message(
        self, 
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(f"You are not the bot owner.", ephemeral=True)

        embed = discord.Embed(
            title="An update has been issued!",
            description=self.bot.patch_notes.format(self.bot.version, self.bot.version),
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
