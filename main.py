import os
import asyncio
import logging
import notifier
from bot import *
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

load_dotenv()
logger = logging.getLogger(__name__)
cookie = os.environ.get("cookie", "")
discord_token = os.environ.get("token", "")
headers = {
    "Cookie": f".ROBLOSECURITY={cookie}"
}

version = "2.8.0"
patch_notes = (Path(__file__).parent / "patch_notes.txt").read_text()

backup_folder = Path(__file__).parent / "database" / "backups"
backup_folder.mkdir(parents=True, exist_ok=True)

api = notifier.API(headers)
bot = RobloxInvitesBot(api, version, patch_notes)
bot.notifier = notifier.TrackerCore(bot)
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
