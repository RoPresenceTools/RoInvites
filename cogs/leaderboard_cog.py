import math
import discord
from discord import app_commands
from discord.ext import commands
from styling.ri_colors import *

class PaginatedLeaderboard(discord.ui.View):
    def __init__(self, bot, author_id, pagin_func, pagin_func_args, entries, title="", user_id=None, place_id=None, per_page=10):
        super().__init__(timeout=120) # testing | should be 120

        self.bot = bot
        self.author_id = author_id
        self.user_id = user_id
        self.place_id = place_id
        self.per_page = per_page
        self.page = 0
        self.max_page = max(0, math.ceil(entries / 10) - 1)
        self.title = title
        self.pagin_func = pagin_func
        self.pagin_func_args = pagin_func_args
        self.thumbnail_url = None
        self.message = None

        self.update_buttons()

    async def on_timeout(self):
        self.first.disabled = True
        self.previous.disabled = True
        self.next.disabled = True
        self.last.disabled = True

        await self.message.edit(
            embed=await self.get_embed(),
            view=self
        )

    async def get_embed(self):
        start = self.page * self.per_page
        items = await self.pagin_func(*self.pagin_func_args, start)

        if self.thumbnail_url is None:
            if self.user_id is not None:
                self.thumbnail_url = await self.bot.api.get_avatar_headshot(self.user_id)
                display_name = await self.bot.user_manager.get_display_name(self.user_id)
                self.title = self.title.replace("{display_name}", display_name)
            elif self.place_id is not None:
                self.thumbnail_url = await self.bot.api.get_game_icon(self.place_id)
                game_name = await self.bot.api.get_game_name(self.place_id)
                self.title = self.title.replace("{game_name}", game_name)

        if not "|ERROR|" in items:
            embed = discord.Embed(
                title=self.title,
                description="\n".join(
                    f"{start + i}. {item}"
                    for i, item in enumerate(items, start=1)
                ),
                color=discord.Color.dark_gold()
            )
            if self.thumbnail_url is not None:
                embed.set_thumbnail(url=self.thumbnail_url)
            embed.set_footer(
                text=f"Page {self.page + 1}/{self.max_page + 1}"
            )
        else:
            embed = discord.Embed(
                title="Error",
                description=items[1],
                color=red
            )
            embed.set_footer(
                text="Page 0/0"
            )

        return embed

    def update_buttons(self):
        self.first.disabled = self.page <= 0
        self.previous.disabled = self.page <= 0
        self.next.disabled = self.page >= self.max_page
        self.last.disabled = self.page >= self.max_page

    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary)
    async def first(self, interaction, button):
        if interaction.user.id == self.author_id:
            self.page = 0
            self.update_buttons()

            await interaction.response.edit_message(
                embed=await self.get_embed(),
                view=self
            )
        else:
            await interaction.response.send_message("You're not the sender of this message!", ephemeral=True)

    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction, button):
        if interaction.user.id == self.author_id:
            self.page -= 1
            self.update_buttons()

            await interaction.response.edit_message(
                embed=await self.get_embed(),
                view=self
            )
        else:
            await interaction.response.send_message("You're not the sender of this message!", ephemeral=True)

    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary)
    async def next(self, interaction, button):
        if interaction.user.id == self.author_id:
            self.page += 1
            self.update_buttons()

            await interaction.response.edit_message(
                embed=await self.get_embed(),
                view=self
            )
        else:
            await interaction.response.send_message("You're not the sender of this message!", ephemeral=True)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary)
    async def last(self, interaction, button):
        if interaction.user.id == self.author_id:
            self.page = self.max_page
            self.update_buttons()

            await interaction.response.edit_message(
                embed=await self.get_embed(),
                view=self
            )
        else:
            await interaction.response.send_message("You're not the sender of this message!", ephemeral=True)

class LeaderboardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    leaderboard = app_commands.Group(
        name="leaderboard",
        description="Leaderboard commands",
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

    game = app_commands.Group(name="game", description="Game-related leaderboard commands", parent=leaderboard)
    user = app_commands.Group(name="user", description="User-related leaderboard commands", parent=leaderboard)
    breakdown_game = app_commands.Group(name="breakdown_game", description="Game related leaderboard commands", parent=leaderboard)
    breakdown_user = app_commands.Group(name="breakdown_user", description="User related leaderboard commands", parent=leaderboard)

    async def user_autocomplete(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> list[app_commands.Choice[str]]:
        users = await interaction.client.user_manager.get_guild_users(interaction.guild)
        return [
            app_commands.Choice(name=user["username"], value=user["user_id"])
            for user in users
            if query.lower() in user["username"].lower()
        ]

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

    @breakdown_user.command(name="all", description="Sends this server's all-time playtime leaderboard")
    async def get_all_paginated(
        self, 
        interaction: discord.Interaction, 
    ):
        entries = await self.bot.leaderboard_manager.get_entries_total_playtimes(interaction.guild)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            pagin_func=self.bot.leaderboard_manager.get_total_playtimes_paginated,
            pagin_func_args=[interaction.guild],
            entries=entries,
            title="All-Time Playtime Leaderboard",
            user_id=None,
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @breakdown_user.command(name="snapshot", description="Sends this server's playtime leaderboard since last snapshot")
    async def get_all_ls_paginated(
        self,
        interaction: discord.Interaction
    ):
        entries = await self.bot.leaderboard_manager.get_entries_ls_total_playtimes(interaction.guild)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            pagin_func=self.bot.leaderboard_manager.get_ls_total_playtimes_paginated,
            pagin_func_args=[interaction.guild],
            entries=entries,
            title="Since-Last-Snapshot Playtime Leaderboard",
            user_id=None,
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @breakdown_game.command(name="all", description="Sends this server's all-time game playtime leaderboard")
    async def get_all_game_paginated(
        self, 
        interaction: discord.Interaction, 
    ):
        entries = await self.bot.leaderboard_manager.get_entries_agg_game_playtimes(interaction.guild)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            pagin_func=self.bot.leaderboard_manager.get_agg_game_playtimes_paginated,
            pagin_func_args=[interaction.guild],
            entries=entries,
            title="All-Time Playtime Leaderboard",
            user_id=None,
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @breakdown_game.command(name="snapshot", description="Sends this server's game playtime leaderboard since last snapshot")
    async def get_all_ls_game_paginated(
        self,
        interaction: discord.Interaction
    ):
        entries = await self.bot.leaderboard_manager.get_entries_agg_ls_game_playtimes(interaction.guild)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            pagin_func=self.bot.leaderboard_manager.get_agg_ls_game_playtimes_paginated,
            pagin_func_args=[interaction.guild],
            entries=entries,
            title="Since-Last-Snapshot Playtime Leaderboard",
            user_id=None,
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @user.command(name="all", description="Shows a user's statistics in a given server for all games")
    @app_commands.autocomplete(user_id=user_autocomplete)
    async def get_user_paginated(
        self, 
        interaction: discord.Interaction, 
        user_id: int
    ):
        entries = await self.bot.leaderboard_manager.get_entries_game_playtimes(interaction.guild, user_id)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            user_id=user_id,
            pagin_func=self.bot.leaderboard_manager.get_game_playtimes_paginated,
            pagin_func_args=[interaction.guild, user_id],
            entries=entries,
            title="{display_name}'s Played Games",
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @user.command(name="snapshot", description="Shows a user's statistics in a given server for all games since last snapshot")
    @app_commands.autocomplete(user_id=user_autocomplete)
    async def get_user_paginated(
        self, 
        interaction: discord.Interaction, 
        user_id: int
    ):
        entries = await self.bot.leaderboard_manager.get_entries_ls_game_playtimes(interaction.guild, user_id)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            user_id=user_id,
            pagin_func=self.bot.leaderboard_manager.get_ls_game_playtimes_paginated,
            pagin_func_args=[interaction.guild, user_id],
            entries=entries,
            title="{display_name}'s Played Games",
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @game.command(name="all", description="Sends this server's all-time playtime leaderboard for a game")
    @app_commands.autocomplete(place_id=all_games_autocomplete)
    async def all_time_game_leaderboard(
        self, 
        interaction: discord.Interaction,
        place_id: int
    ):
        entries = await self.bot.leaderboard_manager.get_entries_game_playtimes_breakdown(interaction.guild, place_id)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            pagin_func=self.bot.leaderboard_manager.get_game_playtimes_breakdown_paginated,
            pagin_func_args=[interaction.guild, place_id],
            entries=entries,
            title="All-Time Playtime Leaderboard for {game_name}",
            place_id=place_id,
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @game.command(name="snapshot", description="Sends this server's playtime leaderboard for a game since the last saved snapshot")
    @app_commands.autocomplete(place_id=all_games_autocomplete)
    async def ls_game_leaderboard(
        self, 
        interaction: discord.Interaction,
        place_id: int
    ):
        entries = await self.bot.leaderboard_manager.get_entries_ls_game_playtimes_breakdown(interaction.guild, place_id)
        view = PaginatedLeaderboard(
            bot=self.bot,
            author_id=interaction.user.id,
            pagin_func=self.bot.leaderboard_manager.get_ls_game_playtimes_breakdown_paginated,
            pagin_func_args=[interaction.guild, place_id],
            entries=entries,
            title="Since-Last-Snapshot Playtime Leaderboard for {game_name}",
            place_id=place_id,
            per_page=10
        )
        await interaction.response.send_message(embed=await view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @leaderboard.command(name="profile", description="Shows a user's statistics in a given server")
    @app_commands.autocomplete(user_id=user_autocomplete)
    async def get_user_profile(
        self, 
        interaction: discord.Interaction, 
        user_id: int
    ):
        try:
            await interaction.response.defer()
            message_title, message_content = await interaction.client.leaderboard_manager.get_user_stats(interaction.guild, user_id)
            embed = discord.Embed(
                title=message_title,
                description=message_content,
                color=discord.Color.dark_gold() if message_title != "Error" else red
            )

            if message_title != "Error":
                thumbnail_url = await interaction.client.api.get_avatar_headshot(user_id)
                if thumbnail_url is not None:
                    embed.set_thumbnail(url=thumbnail_url)
            await interaction.followup.send(embed=embed)
        except:
            import traceback
            traceback.print_exc()

    @leaderboard.command(name="save", description="Saves a snapshot of user data for weekly leaderboards")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def save_period(
        self, 
        interaction: discord.Interaction, 
    ):
        await interaction.response.defer()
        await interaction.client.snapshot_manager.save_snapshot(interaction.guild)
        await interaction.followup.send("Saved the current data to a snapshot!")

    @leaderboard.command(name="remove", description="Removes the last saved user snapshot")
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
    await bot.add_cog(LeaderboardCog(bot))