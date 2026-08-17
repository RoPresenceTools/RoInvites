import os
import asyncio
import notifier
from bot import *
from dotenv import load_dotenv

load_dotenv()
headers = {
    "Cookie": f".ROBLOSECURITY={os.environ["cookie"]}"
}

version = "2.6.0"
patch_notes = """
Updated from __v{0}__ to __v{1}__

**Patch Notes:**
- Leaderboard functions have been moved to their own .sql files
- Since-last-snapshot leaderboards have been fixed
- Other leaderboard fixes

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