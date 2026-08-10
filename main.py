import os
import asyncio
import notifier
from bot import *
from dotenv import load_dotenv

load_dotenv()
headers = {
    "Cookie": f".ROBLOSECURITY={os.environ["cookie"]}"
}

version = "2.5.0"
patch_notes = """
Updated from __v{0}__ to __v{1}__

**Patch Notes:**
- Added avatar headshot images to invite embeds and user stat embeds
- Added Discord usernames to user cards
- Added paginated leaderboards
    - You can now see more than just the top 10!
   - `/leaderboard game_breakdown` gives the server's game playtime leaderboard.
   - `/leaderboard user_breakdown` gives the server's user playtime leaderboard.
   - `/leaderboard game` gives the leaderboard for a specific game.
   - `/leaderboard user` gives the played games of a user in descending order of playtime.
   - `/leaderboard profile` gives a profile card for a given user.
    - This replaces `/server user_stats` and the concept of usercards entirely.
- Migrated `/leaderboard save | remove` to `/snapshot save | remove`
"""

if not os.path.exists("./database/backups/"):
    os.makedirs("./database/backups/")

api = notifier.API(headers)
bot = RobloxInvitesBot(api)
tracker_core = notifier.TrackerCore(bot)
bot.notifier = tracker_core
presence_tracker = notifier.PresenceTracker(bot, version, patch_notes)

async def main():
    try:
        await asyncio.gather(
            bot.start(os.environ["token"]),
            presence_tracker.track()
        )
    except KeyboardInterrupt:
        pass
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        await bot.api.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())