from __future__ import annotations
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from .publisher import post_new_activities
from .scraper import fetch_activities

log = logging.getLogger("myfuture_bot")

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    load_dotenv()

    token, channel_id = discord_settings()
    asyncio.run(publish(token, channel_id))
    return 0

async def publish(token: str, channel_id: int) -> None:
    activities = await fetch_activities()
    log.info("Found %d activities on MyFuture", len(activities))
    await post_new_activities(token, channel_id, activities)


def discord_settings() -> tuple[str, int]:
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    channel_id = os.environ.get("DISCORD_CHANNEL_ID", "").strip()
    return token, int(channel_id)


if __name__ == "__main__":
    sys.exit(main())
