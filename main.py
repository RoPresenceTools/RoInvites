import os
import asyncio
import notifier
from bot import *
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
headers = {
    "Cookie": f".ROBLOSECURITY={os.environ.get("cookie", "")}"
}

version = "2.6.0"
patch_notes = """
Updated from __v{0}__ to __v{1}__

**Patch Notes:**
- Leaderboard functions have been moved to their own .sql files
- Leaderboards will still show after they time out
- Since-last-snapshot leaderboards have been fixed
- Other leaderboard fixes

**Notice:** There is now a temporary cap of 50 users. This will be increased in a future update.
The cap is not new, as Roblox API requests to presences.roblox.com can process a maximum of 50 user IDs at once.
This change just makes it so the bot doesn't malfunction when there are >50 users.
"""

backup_folder = Path(__file__).parent / "database" / "backups"
backup_folder.mkdir(parents=True, exist_ok=True)

api = notifier.API(headers)
bot = RobloxInvitesBot(api, version, patch_notes)
tracker_core = notifier.TrackerCore(bot)
bot.notifier = tracker_core
presence_tracker = notifier.PresenceTracker(bot)

async def main():
    try:
        await asyncio.gather(
            bot.start(os.environ.get("token", "")),
            presence_tracker.track()
        )
    except asyncio.exceptions.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        await bot.api.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
