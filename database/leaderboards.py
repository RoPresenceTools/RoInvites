class LeaderboardManager:
    def __init__(self, pool, bot, api):
        self.pool = pool
        self.bot = bot
        self.api = api

    async def get_leaderboard_position(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            leaderboard_spot = await conn.fetchval(open("database/sql/get_leaderboard_position.sql").read(), guild_user_ids, user_id)

            if leaderboard_spot == None:
                return 0

            return leaderboard_spot

    async def get_ls_leaderboard_position(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            ls_leaderboard_spot = await conn.fetchval(open("database/sql/get_ls_leaderboard_position.sql").read(), snapshot_id, guild_user_ids, user_id)
            
            if ls_leaderboard_spot == None:
                return 0

            return ls_leaderboard_spot

    async def get_entries_total_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_entries_total_playtimes.sql").read(), guild_user_ids)

    async def get_total_playtimes_total(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_total_playtimes_total.sql").read(), guild_user_ids)

    async def get_total_playtimes(self, guild, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_total_playtimes.sql").read(), guild_user_ids, start)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append({"name": name, "playtime": row["total_playtime"]})

            return items

    async def get_entries_ls_total_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_entries_ls_total_playtimes.sql").read(), snapshot_id, guild_user_ids)

    async def get_ls_total_playtimes_total(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_ls_total_playtimes_total.sql").read(), snapshot_id, guild_user_ids)

    async def get_ls_total_playtimes(self, guild, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_ls_total_playtimes.sql").read(), snapshot_id, guild_user_ids, start)

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
            return await conn.fetchval(open("database/sql/get_entries_agg_game_playtimes.sql").read(), guild_user_ids)

    async def get_agg_game_playtimes_total(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_agg_game_playtimes_total.sql").read(), guild_user_ids)

    async def get_agg_game_playtimes(self, guild, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_agg_game_playtimes.sql").read(), guild_user_ids, start)

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
            return await conn.fetchval(open("database/sql/get_entries_agg_ls_game_playtimes.sql").read(), snapshot_id)

    async def get_agg_ls_game_playtimes_total(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_agg_ls_game_playtimes_total.sql").read(), snapshot_id)

    async def get_agg_ls_game_playtimes(self, guild, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_agg_ls_game_playtimes.sql").read(), snapshot_id, start)

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
            return await conn.fetchval(open("database/sql/get_entries_game_playtimes.sql").read(), user_id)

    async def get_game_playtimes_total(self, guild, user_id):
        if guild != "NO_GUILD":
            guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
            if not user_id in guild_user_ids:
                return 0

        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_game_playtimes_total.sql").read(), user_id)

    async def get_game_playtimes(self, guild, user_id, start):
        if guild != "NO_GUILD":
            guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
            if not user_id in guild_user_ids:
                items = [{"error": "That user is not in this server."}]
                return items

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_game_playtimes.sql").read(), user_id, start)

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
            return await conn.fetchval(open("database/sql/get_entries_ls_game_playtimes.sql").read(), snapshot_id, user_id)

    async def get_ls_game_playtimes_total(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if not user_id in guild_user_ids:
            return 0

        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_ls_game_playtimes_total.sql").read(), snapshot_id, user_id)

    async def get_ls_game_playtimes(self, guild, user_id, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if not user_id in guild_user_ids:
            items = [{"error": "That user is not in this server."}]
            return items

        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_ls_game_playtimes.sql").read(), snapshot_id, user_id, start)

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
            return await conn.fetchval(open("database/sql/get_entries_game_playtimes_breakdown.sql").read(), guild_user_ids, place_id)

    async def get_game_playtimes_breakdown_total(self, guild, place_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_game_playtimes_breakdown_total.sql").read(), guild_user_ids, place_id)

    async def get_game_playtimes_breakdown(self, guild, place_id, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_game_playtimes_breakdown.sql").read(), guild_user_ids, place_id, start)

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
            return await conn.fetchval(open("database/sql/get_entries_ls_game_playtimes_breakdown.sql").read(), snapshot_id, place_id)

    async def get_ls_game_playtimes_breakdown_total(self, guild, place_id):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(open("database/sql/get_ls_game_playtimes_breakdown_total.sql").read(), snapshot_id, place_id)

    async def get_ls_game_playtimes_breakdown(self, guild, place_id, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(open("database/sql/get_ls_game_playtimes_breakdown.sql").read(), snapshot_id, place_id, start)

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

    async def persistent_get_user_leaderboard(self, total, total_playtimes, agg_game_playtimes):
        message_content = f"\n**Total Server Playtime:** {total / 3600:.2f}h"
        message_content += f"\n**Playtime for Top 10 Users:**"
        for i, playtime in enumerate(total_playtimes[:10], start=1):
            message_content += f"\n[#{i}] {playtime["name"]} ({playtime["playtime"] / 3600:.2f}h)"

        message_content += f"\n\n**Playtime for Top 10 Games:**"
        for i, game in enumerate(agg_game_playtimes[:10], start=1):
            message_content += f"\n[#{i}] {game["name"]}: {game["playtime"] / 3600:.2f}h"
        
        return message_content

    async def persistent_get_game_leaderboard(self, root_place_id, total, game_playtimes_breakdown):
        await self.api.cache_id(root_place_id)
        name = await self.api.get_game_name(root_place_id)
        message_title = f"Leaderboard for {name}"
        message_content = f"\n**Total Server Playtime:** {total / 3600:.2f}h"

        message_content += f"\n**Playtime for Top 20 Users:**"
        for i, playtime in enumerate(game_playtimes_breakdown[:20], start=1):
            message_content += f"\n[#{i}] {playtime["name"]} ({playtime["playtime"] / 3600:.2f}h)"
        
        return (message_title, message_content)

    async def persistent_get_alltime_user_leaderboard(self, guild):
        total = await self.get_total_playtimes_total(guild)
        total_playtimes = await self.get_total_playtimes(guild, 0)
        agg_game_playtimes = await self.get_agg_game_playtimes(guild, 0)

        message_title = "All-Time Playtime Leaderboard"
        message_content = await self.persistent_get_user_leaderboard(total, total_playtimes, agg_game_playtimes)

        return (message_title, message_content)

    async def persistent_get_ls_user_leaderboard(self, guild):
        ls_total = await self.get_ls_total_playtimes_total(guild)
        ls_total_playtimes = await self.get_ls_total_playtimes(guild, 0)
        ls_agg_game_playtimes = await self.get_agg_ls_game_playtimes(guild, 0)

        if "error" not in ls_total_playtimes[0] and "error" not in ls_agg_game_playtimes[0]:
            message_title = "Playtime Leaderboard since Last Snapshot"
            message_content = await self.persistent_get_user_leaderboard(ls_total, ls_total_playtimes, ls_agg_game_playtimes)
        elif "error" in ls_total_playtimes[0]:
            message_title, message_content = ("Error", ls_total_playtimes[0]["error"])
        elif "error" in ls_agg_game_playtimes[0]:
            message_title, message_content = ("Error", ls_agg_game_playtimes[0]["error"])

        return (message_title, message_content)

    async def persistent_get_alltime_game_leaderboard(self, guild, root_place_id):
        if not await self.bot.stat_manager.check_if_game_played(guild, root_place_id):
            return ("Error", "This game doesn't exist.")

        total = await self.get_game_playtimes_breakdown_total(guild, root_place_id)
        game_playtimes_breakdown = await self.get_game_playtimes_breakdown(guild, root_place_id, 0)

        if "error" not in game_playtimes_breakdown[0]:
            message_title, message_content = await self.persistent_get_game_leaderboard(root_place_id, total, game_playtimes_breakdown)
        else:
            message_title, message_content = ("Error", game_playtimes_breakdown[0]["error"])

        return (message_title, message_content)

    async def persistent_get_ls_game_leaderboard(self, guild, root_place_id):
        if not await self.bot.stat_manager.check_if_game_played(guild, root_place_id):
            return ("Error", "This game doesn't exist.")

        total = await self.get_ls_game_playtimes_breakdown_total(guild, root_place_id)
        ls_game_playtimes_breakdown = await self.get_ls_game_playtimes_breakdown(guild, root_place_id, 0)
        if "error" not in ls_game_playtimes_breakdown[0]:
            message_title, message_content = await self.persistent_get_game_leaderboard(root_place_id, total, ls_game_playtimes_breakdown)
            message_title = f"{message_title} since Last Snapshot"
        else:
            message_title, message_content = ("Error", ls_game_playtimes_breakdown[0]["error"])

        return (message_title, message_content)