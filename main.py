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
- Added a new admin command: `/admin reload`
    - Bot hosters can now reload the bot's cogs and most code without restarting the bot.
  - This command is mainly for development purposes. Bot updates should still be applied manually.
- Added a new admin command: `/admin update_message`
    - Bot hosters can now test to see how an update patch note message looks before pushing said update.
  - This command is mainly for development purposes.
- Migrated `/leaderboard [save | remove]` to `/snapshot [save | remove]`

**NOTE:** The 1.x.x server migration tool has been removed from the GitHub repository.
    - New bot hosters should use the latest stable 2.x.x version. You can still download the migration tool from the 2.4.1 release (source code).
"""

if not os.path.exists("./database/backups/"):
    os.makedirs("./database/backups/")

api = notifier.API(headers)
bot = RobloxInvitesBot(api, version, patch_notes)
tracker_core = notifier.TrackerCore(bot)
bot.notifier = tracker_core
presence_tracker = notifier.PresenceTracker(bot)

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