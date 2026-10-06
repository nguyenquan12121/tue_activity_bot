from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from . import store
from .publisher import post_new_activities
from .scraper import fetch_activities

log = logging.getLogger("myfuture_bot")

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    load_dotenv()

    token = discord_token()
    channel_ids = [int(channel_id) for channel_id in store.get_channels().values()]
    if not channel_ids:
        log.info("No channels set up yet; use /setchannel in a server")
        return 0
    asyncio.run(publish(token, channel_ids))
    return 0

async def publish(token: str, channel_ids: list[int]) -> None:
    activities = await fetch_activities()
    log.info("Found %d activities on MyFuture", len(activities))
    log.info("Posting to %d channels", len(channel_ids))
    await post_new_activities(token, channel_ids, activities)


def discord_token() -> str:
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN is not set")
    return token


if __name__ == "__main__":
    sys.exit(main())
