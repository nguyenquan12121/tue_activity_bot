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
    channels = {
        int(guild_id): int(channel_id) for guild_id, channel_id in store.get_channels().items()
    }
    if not channels:
        log.info("No channels set up yet; use /setchannel in a server")
        return 0
    for guild_id in asyncio.run(publish(token, channels)):
        store.remove_channel(str(guild_id))
        log.info("Removed server %s from the channel list", guild_id)
    return 0

async def publish(token: str, channels: dict[int, int]) -> list[int]:
    activities = await fetch_activities()
    log.info("Found %d activities on MyFuture", len(activities))
    log.info("Posting to %d channels", len(channels))
    return await post_new_activities(token, channels, activities)


def discord_token() -> str:
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN is not set")
    return token


if __name__ == "__main__":
    sys.exit(main())
