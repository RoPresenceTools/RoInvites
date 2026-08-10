import discord
from discord import app_commands
from discord.ext import commands

class SnapshotCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    snapshot = app_commands.Group(
        name="snapshot",
        description="Snapshot-related commands",
        allowed_installs=app_commands.AppInstallationType(
            guild=True,
            user=False
        ),
        allowed_contexts=app_commands.AppCommandContext(
            guild=True,
            dm_channel=False,
            private_channel=False
        )
    )

    @snapshot.command(name="save", description="Saves a snapshot of user data for weekly leaderboards")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def save_period(
        self, 
        interaction: discord.Interaction, 
    ):
        await interaction.response.defer()
        await interaction.client.snapshot_manager.save_snapshot(interaction.guild)
        await interaction.followup.send("Saved the current data to a snapshot!")

    @snapshot.command(name="remove", description="Removes the last saved user snapshot")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_last_period(
        self, 
        interaction: discord.Interaction, 
    ):
        await interaction.response.defer()
        await interaction.client.snapshot_manager.remove_last_snapshot(interaction.guild)
        await interaction.followup.send("Removed the last saved snapshot.")

async def setup(bot: commands.Bot):
    await bot.add_cog(SnapshotCog(bot))