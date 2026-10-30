import aiohttp
import asyncio
import discord
import logging
from styling.ansi import *

logger = logging.getLogger(__name__)

class PresenceTracker:
    def __init__(self, bot):
        self.bot = bot
        self.version = bot.version

    async def track(self):
        logger.info(f"Starting RoInvites v{self.version}")
        logger.info("Waiting for the bot to get ready")
        await self.bot.wait_until_ready()

        saved_version = await self.bot.metadata_manager.get_version()
        if saved_version != self.version:
            for guild in self.bot.guilds:
                announcement_channel = await self.bot.settings_manager.get_channel(guild, "announcement")

                embed = discord.Embed(
                    title="An update has been issued!",
                    description=self.bot.patch_notes.format(saved_version, self.version),
                    color=discord.Color.blue()
                )

                try:
                    channel = self.bot.get_channel(announcement_channel)
                    await channel.send(embed=embed)
                except:
                    pass

            logger.info("Sent update message to all servers")
            await self.bot.metadata_manager.set_version(self.version)

        times_checked = 1
        while True:
            try:
                user_ids = await self.bot.user_manager.get_all_user_ids()
                if len(user_ids) != 0:
                    await self.bot.presence_manager.save_presences("current")
                    for guild in self.bot.guilds:
                        await self.bot.notifier.send_guild_updates(guild)
                    await self.bot.notifier.process_updates()
                    await self.bot.presence_manager.save_presences("old")
                    await self.bot.user_manager.remove_deleted_users()
                await asyncio.sleep(3)
                times_checked += 1
            except aiohttp.client_exceptions.ClientOSError:
                pass
            except aiohttp.ClientResponseError:
                logger.warning("A client response error has occured")
                await asyncio.sleep(10)
            except aiohttp.client_exceptions.ClientConnectorCertificateError:
                logger.exception("Couldn't connect to Roblox's servers. Make sure your certificates are up to date and that your network isn't blocking Roblox")
                await asyncio.sleep(10)
            except aiohttp.client_exceptions.ClientResponseError:
                logger.warning("A client response error has occured")
                await asyncio.sleep(10)