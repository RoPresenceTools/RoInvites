from .load_sql import load_dir

class UserManager:
    def __init__(self, pool, api):
        self.pool = pool
        self.api = api
        self.queries = load_dir("users")

    async def get_display_name(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_display_name"], user_id)

    async def get_username(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_username"], user_id)

    async def get_freeze_status(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_freeze_status"], user_id)

    async def get_freeze_invites_status(self, guild, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_freeze_invites_status"], guild.id, user_id)

    async def get_guild_users(self, guild):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_guild_users"], guild.id)

        return rows

    async def get_guild_user_ids(self, guild):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_guild_user_ids"], guild.id)
        
        user_ids = [row["user_id"] for row in rows]
        return user_ids

    async def get_user_from_discord_id(self, discord_user):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_user_from_discord_id"], discord_user.id)

    async def get_discord_id_from_user(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(self.queries["get_discord_id_from_user"], user_id)

    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_all_users"])
        users = {
            row["user_id"]: row
            for row in rows
        }
        return users

    async def get_all_user_ids(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_all_user_ids"])
        user_ids = [row["user_id"] for row in rows]
        return user_ids

    async def add_user(self, username, discord_user):
        req = await self.api.post_misc("https://users.roblox.com/v1/usernames/users", json={"usernames": [username]})
        if "data" not in req:
            return "This user doesn't exist."
        if len(req["data"]) == 0:
            return "This user doesn't exist."

        user_id = req["data"][0]["id"]
        username = req["data"][0]["name"]
        display_name = req["data"][0]["displayName"]

        async with self.pool.acquire() as conn:
            user_exists_in_ri = await conn.fetchval(self.queries["user_exists_in_ri"], user_id)
            prev_discord = await conn.fetchrow(self.queries["prev_discord"], discord_user.id)
            prev_roblox = await conn.fetchrow(self.queries["prev_roblox"], user_id)

            if not None in (prev_discord, prev_roblox):
                if prev_discord == prev_roblox:
                    return "You've already linked this account with Roblox Invites."
                elif discord_user.id != prev_roblox["discord_id"]:
                    return "This account has already been linked by someone else."
                elif prev_discord["user_id"] != user_id:
                    return "This account has already been linked by someone else."

            if prev_roblox is not None:
                if discord_user.id != prev_roblox["discord_id"]:
                    return "Someone else already linked this account."

            if prev_discord is not None:
                if prev_discord["user_id"] != user_id:
                    return "You have already linked a different account."

            if not user_exists_in_ri:
                user_data = await self.api.get_misc(f"https://users.roblox.com/v1/users/{user_id}")
                if user_data["description"].lower().strip() != "i confirm that i am joining the invites program.":
                    return f"**You must verify that the following account (@{username}) is yours.**\nPlease set `I confirm that I am joining the Invites program.` as your Roblox account description and try again.\nYou can edit your description [here](<https://www.roblox.com/users/profile/edit>)."

            await conn.execute(self.queries["add_user"], user_id, discord_user.id, username, display_name)
        return True

    async def remove_user(self, discord_user):
        async with self.pool.acquire() as conn:
            user_id = await self.get_user_from_discord_id(discord_user)
            if user_id is None:
                return False

            await conn.execute(self.queries["remove_user"], user_id)
        return True

    async def remove_user_id(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["remove_user"], user_id)
        return True

    async def link_user(self, discord_user, guild):
        user_id = await self.get_user_from_discord_id(discord_user)
        if user_id is None:
            return "You don't have a Roblox account associated with Roblox Invites.\nAdd one with `/user add`!"

        async with self.pool.acquire() as conn:
            user_exists_in_guild = await conn.fetchval(self.queries["user_exists_in_guild"], guild.id, user_id)

            if user_exists_in_guild:
                return f"You are already in in this server."

            await conn.execute(self.queries["link_user"], guild.id, user_id)
        return True

    async def unlink_user(self, discord_user, guild):
        async with self.pool.acquire() as conn:
            user_id = await self.get_user_from_discord_id(discord_user)
            if user_id is None:
                return False

            await conn.execute(self.queries["unlink_user"], guild.id, user_id)
        return True

    async def modify_server_invites(self, discord_user, guild, value):
        user_id = await self.get_user_from_discord_id(discord_user)
        if user_id is None:
            return "You don't have a Roblox account associated with Roblox Invites.\nAdd one with `/user add`!"

        async with self.pool.acquire() as conn:
            user_exists_in_guild = await conn.fetchval(self.queries["user_exists_in_guild"], guild.id, user_id)

            if not user_exists_in_guild:
                return f"You are not in this server."

            await conn.execute(self.queries["modify_server_invites"], guild.id, user_id, value)
        return True

    async def modify_freeze_user(self, discord_user, value):
        user_id = await self.get_user_from_discord_id(discord_user)
        if user_id is None:
            return "You don't have a Roblox account associated with Roblox Invites.\nAdd one with `/user add`!"

        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["modify_freeze_user"], user_id, value)
        return True

    async def remove_deleted_users(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(self.queries["get_deleted_users"])
            if rows is None:
                return
            deleted_user_ids = [row["user_id"] for row in rows]

            categories = ["subscriptions", "users", "currently_playing", "game_playtimes", "total_playtimes", "presences", "old_presences"]
            for category in categories:
                await conn.execute(self.queries[f"remove_deleted_{category}"], deleted_user_ids)

    async def update_user_info(self, discord_user):
        async with self.pool.acquire() as conn:
            user_id = await self.get_user_from_discord_id(discord_user)
            if user_id is None:
                return f"You don't have a Roblox account associated with Roblox Invites.\nAdd one with `/user add`!"

        req = await self.api.post_misc("https://users.roblox.com/v1/users", json={"userIds": [user_id]})
        if "data" not in req:
            return "Couldn't update your user info."
        if len(req["data"]) == 0:
            return "Couldn't update your user info."
        username = req["data"][0]["name"]
        display_name = req["data"][0]["displayName"]

        async with self.pool.acquire() as conn:
            await conn.execute(self.queries["update_user_info"], user_id, discord_user.id, username, display_name)
        return True
