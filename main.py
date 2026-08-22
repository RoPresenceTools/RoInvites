import asyncio
import notifier
from bot import *
from dotenv import load_dotenv
from pathlib import Path

cookie = Path("/run/secrets/roblosecurity").read_text().strip()
discord_token = Path("/run/secrets/discord_token").read_text().strip()

load_dotenv()
headers = {
    "Cookie": f".ROBLOSECURITY={cookie}"
}

version = "3.0.0"
patch_notes = """
Updated from __v{0}__ to __v{1}__

**Patch Notes:**
- Add Docker container support
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
            bot.start(discord_token),
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
