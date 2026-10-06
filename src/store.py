from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

CHANNELS_KEY = "channels"

def set_channel(guild_id: str, channel_id: str) -> None:
    command("HSET", CHANNELS_KEY, guild_id, channel_id)


def remove_channel(guild_id: str) -> None:
    command("HDEL", CHANNELS_KEY, guild_id)


def get_channels() -> dict[str, str]:
    flat = command("HGETALL", CHANNELS_KEY) or []
    return dict(zip(flat[::2], flat[1::2], strict=True))


def command(*args: str) -> Any:
    request = urllib.request.Request(
        os.environ["UPSTASH_REDIS_REST_URL"],
        data=json.dumps(args).encode(),
        headers={"Authorization": f"Bearer {os.environ['UPSTASH_REDIS_REST_TOKEN']}"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)["result"]
