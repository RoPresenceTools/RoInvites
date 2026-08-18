import discord
from discord import app_commands
from discord.ext import commands
from styling.ri_colors import *

class PersistentLeaderboardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    persistent_leaderboard = app_commands.Group(
        name="persistent",
        description="Persistent leaderboard commands",
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
    game = app_commands.Group(name="game", description="Game-related persistent leaderboard commands", parent=persistent_leaderboard)

    async def all_games_autocomplete(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> list[app_commands.Choice[str]]:
        game_list = await self.bot.api.get_cached_games(interaction.guild, query)

        return [
            app_commands.Choice(name=game["game_name"], value=game["root_place_id"])
            for game in game_list
        ]

    @persistent_leaderboard.command(name="all", description="Sends this server's all-time playtime leaderboard")
    async def all_time_user_leaderboard(
        self, 
        interaction: discord.Interaction
    ):
        (message_title, message_content) = await interaction.client.leaderboard_manager.persistent_get_alltime_user_leaderboard(interaction.guild)
        embed = discord.Embed(
            title=message_title,
            description=message_content,
            color=discord.Color.dark_gold()
        )
        await interaction.response.send_message(embed=embed)

    @persistent_leaderboard.command(name="snapshot", description="Sends this server's playtime leaderboard since last snapshot")
    async def ls_leaderboard(
        self,
        interaction: discord.Interaction
    ):
        (message_title, message_content) = await interaction.client.leaderboard_manager.persistent_get_ls_user_leaderboard(interaction.guild)
        embed = discord.Embed(
            title=message_title,
            description=message_content,
            color=discord.Color.dark_gold() if message_title != "Error" else red
        )
        await interaction.response.send_message(embed=embed)

    @game.command(name="all", description="Sends this server's all-time playtime leaderboard for a game")
    @app_commands.autocomplete(place_id=all_games_autocomplete)
    async def all_time_game_leaderboard(
        self, 
        interaction: discord.Interaction,
        place_id: int
    ):
        (message_title, message_content) = await interaction.client.leaderboard_manager.persistent_get_alltime_game_leaderboard(interaction.guild, place_id)
        embed = discord.Embed(
            title=message_title,
            description=message_content,
            color=discord.Color.dark_gold() if message_title != "Error" else red
        )
        await interaction.response.send_message(embed=embed)

    @game.command(name="snapshot", description="Sends this server's playtime leaderboard for a game since the last saved snapshot")
    @app_commands.autocomplete(place_id=all_games_autocomplete)
    async def ls_game_leaderboard(
        self, 
        interaction: discord.Interaction,
        place_id: int
    ):
        try:
            (message_title, message_content) = await interaction.client.leaderboard_manager.persistent_get_ls_game_leaderboard(interaction.guild, place_id)
            embed = discord.Embed(
                title=message_title,
                description=message_content,
                color=discord.Color.dark_gold() if message_title != "Error" else red
            )
            await interaction.response.send_message(embed=embed)
        except:
            import traceback
            traceback.print_exc()
        
async def setup(bot: commands.Bot):
    await bot.add_cog(PersistentLeaderboardCog(bot))