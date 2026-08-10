from datetime import datetime

class LeaderboardManager:
    def __init__(self, pool, bot, api):
        self.pool = pool
        self.bot = bot
        self.api = api

    async def get_leaderboard_position(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            leaderboard_spot = await conn.fetchval("""
                SELECT rank
                FROM (
                    SELECT
                        user_id,
                        total_playtime,
                        RANK() OVER (ORDER BY total_playtime DESC) AS rank
                    FROM (
                        SELECT
                            t.user_id,
                            COALESCE(t.total_playtime, 0)
                            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
                        FROM total_playtimes t
                        LEFT JOIN currently_playing cp
                            ON cp.user_id = t.user_id
                        WHERE t.user_id = ANY($1)
                    ) playtimes
                ) ranked
                WHERE user_id = $2
            """, guild_user_ids, user_id)

            if leaderboard_spot == None:
                return 0

            return leaderboard_spot

    async def get_ls_leaderboard_position(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            ls_leaderboard_spot = await conn.fetchval("""
                SELECT rank
                FROM (
                    SELECT
                        user_id,
                        total_playtime,
                        RANK() OVER (ORDER BY total_playtime DESC) AS rank
                    FROM (
                        SELECT
                            s.user_id,
                            t.total_playtime
                            - COALESCE(s.total_playtime, 0)
                            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
                        FROM total_playtime_snapshots s
                        LEFT JOIN total_playtimes t
                            ON t.user_id = s.user_id
                        LEFT JOIN currently_playing cp
                            ON cp.user_id = s.user_id
                        WHERE s.snapshot_id = $1
                        AND s.user_id = ANY($2)
                    ) playtimes
                )
                WHERE user_id = $3
            """, snapshot_id, guild_user_ids, user_id)
            
            if ls_leaderboard_spot == None:
                return 0

            return ls_leaderboard_spot

    async def get_entries_total_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        t.user_id,
                        COALESCE(t.total_playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
                    FROM total_playtimes t
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = t.user_id
                    WHERE t.user_id = ANY($1)
                ) playtimes
            """, guild_user_ids)

    async def get_total_playtimes_paginated(self, guild, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    user_id,
                    total_playtime,
                    RANK() OVER (ORDER BY total_playtime DESC) AS rank
                FROM (
                    SELECT
                        t.user_id,
                        COALESCE(t.total_playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
                    FROM total_playtimes t
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = t.user_id
                    WHERE t.user_id = ANY($1)
                ) playtimes
                LIMIT 10
                OFFSET {start}
            """, guild_user_ids)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append(f"{name} - {(row["total_playtime"] / 3600):.2f}h")

            return items

    async def get_entries_ls_total_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        s.user_id,
                        t.total_playtime
                        - COALESCE(s.total_playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
                    FROM total_playtime_snapshots s
                    LEFT JOIN total_playtimes t
                        ON t.user_id = s.user_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                    WHERE s.snapshot_id = $1
                    AND s.user_id = ANY($2)
                ) playtimes
            """, snapshot_id, guild_user_ids)

    async def get_ls_total_playtimes_paginated(self, guild, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    user_id,
                    total_playtime,
                    RANK() OVER (ORDER BY total_playtime DESC) AS rank
                FROM (
                    SELECT
                        s.user_id,
                        t.total_playtime
                        - COALESCE(s.total_playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
                    FROM total_playtime_snapshots s
                    LEFT JOIN total_playtimes t
                        ON t.user_id = s.user_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                    WHERE s.snapshot_id = $1
                    AND s.user_id = ANY($2)
                ) playtimes
                LIMIT 10
                OFFSET {start}
            """, snapshot_id, guild_user_ids)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append(f"{name} - {(row["total_playtime"] / 3600):.2f}h")

            return items

    async def get_entries_game_playtimes(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM game_playtimes
                WHERE user_id = $1
            """, user_id)

    async def get_game_playtimes_paginated(self, user_id, start):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    user_id,
                    place_id,
                    playtime,
                    RANK() OVER (ORDER BY playtime DESC) AS rank
                FROM (
                    SELECT
                        g.user_id,
                        g.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS playtime
                    FROM game_playtimes g
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = g.user_id
                        AND cp.place_id = g.place_id
                    WHERE g.user_id = $1
                ) games_ranked
                LIMIT 10
                OFFSET {start}
            """, user_id)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append(f"{name} - {(row["playtime"] / 3600):.2f}h")

            return items

    async def get_entries_ls_game_playtimes(self, guild, user_id):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        s.user_id,
                        s.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                        - s.playtime AS playtime
                    FROM game_playtime_snapshots s
                    LEFT JOIN game_playtimes g
                        ON g.user_id = s.user_id
                        AND g.place_id = s.place_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                        AND cp.place_id = s.place_id
                    WHERE s.snapshot_id = $1
                    AND s.user_id = $2
                ) games_ranked
                WHERE playtime > 0
            """, snapshot_id, user_id)

    async def get_ls_game_playtimes_paginated(self, guild, user_id, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    user_id,
                    place_id,
                    playtime,
                    RANK() OVER (ORDER BY playtime DESC) AS rank
                FROM (
                    SELECT
                        s.user_id,
                        s.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                        - s.playtime AS playtime
                    FROM game_playtime_snapshots s
                    LEFT JOIN game_playtimes g
                        ON g.user_id = s.user_id
                        AND g.place_id = s.place_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                        AND cp.place_id = s.place_id
                    WHERE s.snapshot_id = $1
                    AND s.user_id = $2
                ) games_ranked
                WHERE playtime > 0
                LIMIT 10
                OFFSET {start}
            """, snapshot_id, user_id)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append(f"{name} - {(row["playtime"] / 3600):.2f}h")

            return items

    async def get_entries_agg_game_playtimes(self, guild):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        g.place_id,
                        SUM(
                            COALESCE(g.playtime, 0)
                            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                        ) AS playtime
                    FROM game_playtimes g
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = g.user_id
                        AND cp.place_id = g.place_id
                    WHERE g.user_id = ANY($1)
                    GROUP BY g.place_id
                ) games_ranked
            """, guild_user_ids)

    async def get_agg_game_playtimes_paginated(self, guild, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    place_id,
                    playtime,
                    RANK() OVER (ORDER BY playtime DESC) AS rank
                FROM (
                    SELECT
                        g.place_id,
                        SUM(
                            COALESCE(g.playtime, 0)
                            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                        ) AS playtime
                    FROM game_playtimes g
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = g.user_id
                        AND cp.place_id = g.place_id
                    WHERE g.user_id = ANY($1)
                    GROUP BY g.place_id
                ) games_ranked
                LIMIT 10
                OFFSET {start}
            """, guild_user_ids)

            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append(f"{name} - {(row["playtime"] / 3600):.2f}h")

            return items

    async def get_entries_agg_ls_game_playtimes(self, guild):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        s.place_id,
                        SUM(
                            COALESCE(g.playtime, 0)
                            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                            - s.playtime
                        ) AS playtime
                    FROM game_playtime_snapshots s
                    LEFT JOIN game_playtimes g
                        ON g.user_id = s.user_id
                        AND g.place_id = s.place_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                        AND cp.place_id = s.place_id
                    WHERE s.snapshot_id = $1
                    GROUP BY s.place_id
                ) games_ranked
                WHERE playtime > 0
            """, snapshot_id)

    async def get_agg_ls_game_playtimes_paginated(self, guild, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    place_id,
                    playtime,
                    RANK() OVER (ORDER BY playtime DESC) AS rank
                FROM (
                    SELECT
                        s.place_id,
                        SUM(
                            COALESCE(g.playtime, 0)
                            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                            - s.playtime
                        ) AS playtime
                    FROM game_playtime_snapshots s
                    LEFT JOIN game_playtimes g
                        ON g.user_id = s.user_id
                        AND g.place_id = s.place_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                        AND cp.place_id = s.place_id
                    WHERE s.snapshot_id = $1
                    GROUP BY s.place_id
                ) games_ranked
                WHERE playtime > 0
                LIMIT 10
                OFFSET {start}
            """, snapshot_id)


            items = []
            for row in rows:
                name = await self.bot.api.get_game_name(row["place_id"])
                items.append(f"{name} - {(row["playtime"] / 3600):.2f}h")

            return items

    async def get_entries_game_playtimes_breakdown(self, guild, place_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        g.user_id,
                        g.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS playtime
                    FROM game_playtimes g
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = g.user_id
                        AND cp.place_id = g.place_id
                    WHERE g.user_id = ANY($1)
                    AND g.place_id = $2
                ) games_ranked
            """, guild_user_ids, place_id)

    async def get_game_playtimes_breakdown_paginated(self, guild, place_id, start):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    user_id,
                    place_id,
                    playtime,
                    RANK() OVER (ORDER BY playtime DESC) AS rank
                FROM (
                    SELECT
                        g.user_id,
                        g.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS playtime
                    FROM game_playtimes g
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = g.user_id
                        AND cp.place_id = g.place_id
                    WHERE g.user_id = ANY($1)
                    AND g.place_id = $2
                ) games_ranked
                LIMIT 10
                OFFSET {start}
            """, guild_user_ids, place_id)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append(f"{name} - {(row["playtime"] / 3600):.2f}h")

            return items

    async def get_entries_ls_game_playtimes_breakdown(self, guild, place_id):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        s.user_id,
                        s.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                        - s.playtime AS playtime
                    FROM game_playtime_snapshots s
                    LEFT JOIN game_playtimes g
                        ON g.user_id = s.user_id
                        AND g.place_id = s.place_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                        AND cp.place_id = s.place_id
                    WHERE s.snapshot_id = $1
                    AND g.place_id = $2
                ) games_ranked
            """, snapshot_id, place_id)

    async def get_ls_game_playtimes_breakdown_paginated(self, guild, place_id, start):
        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    user_id,
                    place_id,
                    playtime,
                    RANK() OVER (ORDER BY playtime DESC) AS rank
                FROM (
                    SELECT
                        s.user_id,
                        s.place_id,
                        COALESCE(g.playtime, 0)
                        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
                        - s.playtime AS playtime
                    FROM game_playtime_snapshots s
                    LEFT JOIN game_playtimes g
                        ON g.user_id = s.user_id
                        AND g.place_id = s.place_id
                    LEFT JOIN currently_playing cp
                        ON cp.user_id = s.user_id
                        AND cp.place_id = s.place_id
                    WHERE s.snapshot_id = $1
                    AND s.place_id = $2
                ) games_ranked
                WHERE playtime > 0
                LIMIT 10
                OFFSET {start}
            """, snapshot_id, place_id)

            items = []
            for row in rows:
                name = await self.bot.user_manager.get_display_name(row["user_id"])
                items.append(f"{name} - {(row["playtime"] / 3600):.2f}h")

            return items

    async def get_user_leaderboard(self, total_playtimes, agg_game_playtimes):
        players = 0
        total = sum([playtime["total_playtime"] for playtime in total_playtimes])

        message_content = f"\n**Total Server Playtime:** {total / 3600:.2f}h"
        message_content += f"\n**Playtime for Top 10 Users:**"
        for playtime in total_playtimes[:10]:
            display_name = await self.bot.user_manager.get_display_name(playtime["user_id"])
            message_content += f"\n[#{playtime["rank"]}] {display_name} ({playtime["total_playtime"] / 3600:.2f}h)"

        message_content += f"\n\n**Playtime for Top 10 Games:**"
        for game in agg_game_playtimes[:10]:
            if game["playtime"] > 0:
                await self.api.cache_id(game["place_id"])
                name = await self.api.get_game_name(game["place_id"])
                message_content += f"\n[#{game["rank"]}] {name}: {game["playtime"] / 3600:.2f}h"
                players += 1
        if players == 0:
            message_content += "\nNo one has played any games yet."
        
        return message_content

    async def get_game_leaderboard(self, root_place_id, game_playtimes_breakdown):
        players = 0
        total = sum([playtime["playtime"] for playtime in game_playtimes_breakdown])

        await self.api.cache_id(root_place_id)
        name = await self.api.get_game_name(root_place_id)
        message_title = f"Leaderboard for {name}"
        message_content = f"\n**Total Server Playtime:** {total / 3600:.2f}h"

        message_content += f"\n**Playtime for Top 20 Users:**"
        for playtime in game_playtimes_breakdown[:20]:
            if playtime["playtime"] > 0:
                display_name = await self.bot.user_manager.get_display_name(playtime["user_id"])
                message_content += f"\n[#{playtime["rank"]}] {display_name} ({playtime["playtime"] / 3600:.2f}h)"
                players += 1
        if players == 0:
            message_content += "\nNo one has played this game yet."
        
        return (message_title, message_content)

    async def get_user_stats(self, guild, user_id):
        guild_user_ids = await self.bot.user_manager.get_guild_user_ids(guild)
        if user_id not in guild_user_ids:
            return ("Error", "That user isn't in this server.")

        discord_user_id = await self.bot.user_manager.get_discord_id_from_user(user_id)
        leaderboard_spot = await self.get_leaderboard_position(guild, user_id)
        game_playtimes = await self.get_game_playtimes_paginated(user_id, 0)

        snapshot_id = await self.bot.snapshot_manager.get_latest_snapshot_id(guild)
        ls_leaderboard_spot = await self.get_ls_leaderboard_position(guild, user_id)
        ls_game_playtimes = await self.get_ls_game_playtimes_paginated(guild, user_id, 0)

        total = await self.bot.stat_manager.get_total_playtime(user_id)
        display_name = await self.bot.user_manager.get_display_name(user_id)
        username = await self.bot.user_manager.get_username(user_id)

        message_title = f"{display_name}'s usercard"

        message_content = "**Your Info:**"
        message_content += f"\nRoblox username: @{username}"
        message_content += f"\nDiscord username: <@{discord_user_id}>"

        message_content += "\n\n**Your Playtimes:**"
        message_content += f"\nOverall Playtime: {total / 3600:.2f}h"

        message_content += "\n\n**Your Standings:**"
        message_content += f"\nOverall Leaderboard Position: #{leaderboard_spot}"
        message_content += f"\nSince-Last-Snapshot Leaderboard Position: #{ls_leaderboard_spot}"

        overall_games = 0
        message_content += "\n\n**Your Top 5 Games Overall:**"
        for game in game_playtimes[:5]:
            if game["playtime"] > 0:
                await self.api.cache_id(game["place_id"])
                name = await self.api.get_game_name(game["place_id"])
                message_content += f"\n[#{game["rank"]}] {name}: {game["playtime"] / 3600:.2f}h"
                overall_games += 1
        if overall_games == 0:
            message_content += "\nYou haven't played any games yet."

        ls_games = 0
        message_content += f"\n\n**Your Top 5 Games since Last Snapshot:**"
        if snapshot_id != None:
            for game in ls_game_playtimes[:5]:
                if game["playtime"] > 0:
                    await self.api.cache_id(game["place_id"])
                    name = await self.api.get_game_name(game["place_id"])
                    message_content += f"\n[#{game["rank"]}] {name}: {game["playtime"] / 3600:.2f}h"
                    ls_games += 1
        else:
            message_content += "\nNo snapshots have been saved."
        if ls_games == 0 and snapshot_id != None:
            message_content += "\nYou haven't played any games since the last snapshot was taken."

        return (message_title, message_content)

    async def get_user_stats_dms(self, discord_user):
        user_id = await self.bot.user_manager.get_user_from_discord_id(discord_user)

        discord_user_id = await self.bot.user_manager.get_discord_id_from_user(user_id)
        game_playtimes = await self.get_game_playtimes_paginated(user_id, 0)

        total = await self.bot.stat_manager.get_total_playtime(user_id)
        display_name = await self.bot.user_manager.get_display_name(user_id)
        username = await self.bot.user_manager.get_username(user_id)

        message_title = f"{display_name}'s usercard"

        message_content = "**Your Info:**"
        message_content += f"\nRoblox username: @{username}"
        message_content += f"\nDiscord username: <@{discord_user_id}>"

        message_content += f"\n\n**Your Playtimes:**"
        message_content += f"\nOverall Playtime: {total / 3600:.2f}h"

        overall_games = 0
        message_content += f"\n\n**Your Top 10 Games Overall:**"
        for game in game_playtimes[:10]:
            if game["playtime"] > 0:
                await self.api.cache_id(game["place_id"])
                name = await self.api.get_game_name(game["place_id"])
                message_content += f"\n[#{game["rank"]}] {name}: {game["playtime"] / 3600:.2f}h"
                overall_games += 1
        if overall_games == 0:
            message_content += "\nYou haven't played any games yet."

        return (message_title, message_content)