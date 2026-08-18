import database

class LeaderboardManager:
    def __init__(self, pool, bot, api):
        self.pool = pool
        self.bot = bot
        self.api = api
        self.queries = database.load_sql("leaderboards")

    async def get_leaderboard_position(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            leaderboard_spot = await conn.fetchval(self.queries["get_leaderboard_position"], guild_user_ids, user_id)

            if leaderboard_spot == None:
                return 0

            return leaderboard_spot

    async def get_ls_leaderboard_position(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            ls_leaderboard_spot = await conn.fetchval(self.queries["get_ls_leaderboard_position"], snapshot_id, guild_user_ids, user_id)
            
            if ls_leaderboard_spot == None:
                return 0

            return ls_leaderboard_spot

    async def get_entries_total_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_total_playtimes"], guild_user_ids)

    async def get_total_total_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_total_playtimes"], guild_user_ids)

    async def get_total_playtimes(self, guild, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_total_playtimes"], guild_user_ids, start)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append({"name": name, "playtime": row["total_playtime"]})

            return items

    async def get_entries_ls_total_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_ls_total_playtimes"], snapshot_id, guild_user_ids)

    async def get_total_ls_total_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_ls_total_playtimes"], snapshot_id, guild_user_ids)

    async def get_ls_total_playtimes(self, guild, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_ls_total_playtimes"], snapshot_id, guild_user_ids, start)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append({"name": name, "playtime": row["total_playtime"]})
            if len(rows) == 0:
                items.append({"error": "No one has played any game since the last snapshot."})

            return items

    async def get_entries_agg_game_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_agg_game_playtimes"], guild_user_ids)

    async def get_total_agg_game_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_agg_game_playtimes"], guild_user_ids)

    async def get_agg_game_playtimes(self, guild, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_agg_game_playtimes"], guild_user_ids, start)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append({"name": name, "playtime": row["playtime"]})
            if len(rows) == 0:
                items.append({"error": "No one has played any games yet."})

            return items

    async def get_entries_agg_ls_game_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_agg_ls_game_playtimes"], snapshot_id)

    async def get_total_agg_ls_game_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_agg_ls_game_playtimes"], snapshot_id)

    async def get_agg_ls_game_playtimes(self, guild, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_agg_ls_game_playtimes"], snapshot_id, start)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append({"name": name, "playtime": row["playtime"]})
            if len(rows) == 0:
                items.append("|ERROR|")
                items.append("No one has played any games since the last snapshot.")

            return items

    async def get_entries_game_playtimes(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if not user_id in guild_user_ids:
            return 0

        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_game_playtimes"], user_id)

    async def get_total_game_playtimes(self, guild, user_id):
        if guild != "NO_GUILD":
            guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
            if not user_id in guild_user_ids:
                return 0

        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_game_playtimes"], user_id)

    async def get_game_playtimes(self, guild, user_id, start):
        if guild != "NO_GUILD":
            guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
            if not user_id in guild_user_ids:
                items = [{"error": "That user is not in this server."}]
                return items

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_game_playtimes"], user_id, start)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append({"name": name, "playtime": row["playtime"]})

            return items

    async def get_entries_ls_game_playtimes(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if not user_id in guild_user_ids:
            return 0

        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_ls_game_playtimes"], snapshot_id, user_id)

    async def get_total_ls_game_playtimes(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if not user_id in guild_user_ids:
            return 0

        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_ls_game_playtimes"], snapshot_id, user_id)

    async def get_ls_game_playtimes(self, guild, user_id, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if not user_id in guild_user_ids:
            items = [{"error": "That user is not in this server."}]
            return items

        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_ls_game_playtimes"], snapshot_id, user_id, start)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append({"name": name, "playtime": row["playtime"]})
            if len(rows) == 0:
                items.append({"error": "This user hasn't played any games since the last snapshot."})

            return items

    async def get_entries_game_playtimes_breakdown(self, guild, place_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_game_playtimes_breakdown"], guild_user_ids, place_id)

    async def get_total_game_playtimes_breakdown(self, guild, place_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_game_playtimes_breakdown"], guild_user_ids, place_id)

    async def get_game_playtimes_breakdown(self, guild, place_id, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_game_playtimes_breakdown"], guild_user_ids, place_id, start)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append({"name": name, "playtime": row["playtime"]})
            if len(rows) == 0:
                game_name = await self.bot.api.get_game_name(place_id)
                items.append({"error": f"No one has played *{game_name}* yet."})

            return items

    async def get_entries_ls_game_playtimes_breakdown(self, guild, place_id):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_entries_ls_game_playtimes_breakdown"], snapshot_id, place_id)

    async def get_total_ls_game_playtimes_breakdown(self, guild, place_id):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_total_ls_game_playtimes_breakdown"], snapshot_id, place_id)

    async def get_ls_game_playtimes_breakdown(self, guild, place_id, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_ls_game_playtimes_breakdown"], snapshot_id, place_id, start)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append({"name": name, "playtime": row["playtime"]})
            if len(rows) == 0:
                game_name = await self.bot.api.get_game_name(place_id)
                items.append({"error": f"No one has played *{game_name}* since the last snapshot."})

            return items

    async def get_user_stats(self, user_id=None, discord_user=None, guild=None, mode=None):
        if mode == "server":
            guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
            if user_id not in guild_user_ids:
                return ("Error", "That user is not in this server.")
        else:
            user_id = await self.bot.user_manager.get_user_from_discord_id(discord_user)
            if user_id is None:
                return ("Error", "You don't have a Roblox account associated with Roblox Invites.\nAdd one with `/user add`!")

        discord_user_id = await self.bot.user_manager.get_discord_id_from_user(user_id)
        game_playtimes = await self.get_game_playtimes("NO_GUILD", user_id, 0)

        if mode == "server":
            snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
            leaderboard_spot = await self.get_leaderboard_position(guild, user_id)
            ls_leaderboard_spot = await self.get_ls_leaderboard_position(guild, user_id)
            ls_game_playtimes = await self.get_ls_game_playtimes(guild, user_id, 0)

        total = await self.bot.stat_manager.get_total_playtime(user_id)
        display_name = await self.bot.user_manager.get_display_name(user_id)
        username = await self.bot.user_manager.get_username(user_id)

        message_title = f"{display_name}'s profile"

        message_content = "**Your Info:**"
        message_content += f"\nRoblox username: @{username}"
        message_content += f"\nDiscord username: <@{discord_user_id}>"

        playtime = await self.bot.stat_manager.get_playtime_str(playtime=total)
        message_content += "\n\n**Your Playtimes:**"
        message_content += f"\nOverall Playtime: {playtime}"

        if mode == "server":
            message_content += "\n\n**Your Standings:**"
            message_content += f"\nOverall Leaderboard Position: #{leaderboard_spot}"
            message_content += f"\nSince-Last-Snapshot Leaderboard Position: #{ls_leaderboard_spot}"

        games_to_list = 5 if mode == "server" else 10
        message_content += f"\n\n**Your Top {games_to_list} Games Overall:**"
        if len(game_playtimes) == 0:
            message_content += f"\nYou haven't played any games yet."
        elif "error" not in game_playtimes[:games_to_list][0]:
            for i, item in enumerate(game_playtimes[:games_to_list]):
                playtime_str = await self.bot.stat_manager.get_playtime_str(playtime=item["playtime"])
                message_content += f"\n{i}. {item["name"]} - {playtime_str}"
        else:
            message_content += f"\n{game_playtimes[:games_to_list][0]["error"]}"

        if mode == "server":
            message_content += f"\n\n**Your Top 5 Games since Last Snapshot:**"
            if snapshot_id is not None:
                if len(ls_game_playtimes) == 0:
                    message_content += "\nYou haven't played any games since the last snapshot was taken."
                elif "error" not in ls_game_playtimes[:5][0]:
                    for i, item in enumerate(ls_game_playtimes[:5]):
                        playtime_str = await self.bot.stat_manager.get_playtime_str(playtime=item["playtime"])
                        message_content += f"\n{i}. {item["name"]} - {playtime_str}"
                else:
                    message_content += "\nYou haven't played any games since the last snapshot was taken."
            else:
                message_content += "\nNo snapshots have been saved."

        return (message_title, message_content)
