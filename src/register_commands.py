from __future__ import annotations

import json
import os
import urllib.request

from dotenv import load_dotenv

MANAGE_GUILD = 1 << 5
GUILD_TEXT, GUILD_ANNOUNCEMENT = 0, 5
CHANNEL_OPTION = 7

COMMANDS = [
    {
        "name": "setchannel",
        "description": "Post MyFuture activities in a channel",
        "default_member_permissions": str(MANAGE_GUILD),
        "contexts": [0],  # servers only
        "options": [
            {
                "name": "channel",
                "description": "Where to post",
                "type": CHANNEL_OPTION,
                "channel_types": [GUILD_TEXT, GUILD_ANNOUNCEMENT],
                "required": True,
            }
        ],
    },
    {
        "name": "stop",
        "description": "Stop posting MyFuture activities in this server",
        "default_member_permissions": str(MANAGE_GUILD),
        "contexts": [0],
    },
]


def main() -> None:
    load_dotenv()
    request = urllib.request.Request(
        f"https://discord.com/api/v10/applications/{os.environ['DISCORD_APP_ID']}/commands",
        data=json.dumps(COMMANDS).encode(),
        method="PUT",
        headers={
            "Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (myfuture-discord-bot, 0.1.0)",
        },
    )
    with urllib.request.urlopen(request) as response:
        registered = json.load(response)
    print("Registered:", ", ".join(f"/{command['name']}" for command in registered))


if __name__ == "__main__":
    main()