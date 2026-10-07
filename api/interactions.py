from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # make `src` importable on Vercel
from src import store

log = logging.getLogger(__name__)

POST_WORKFLOW = "post.yml"
PING = 1
APPLICATION_COMMAND = 2
PONG = 1
CHANNEL_MESSAGE = 4
EPHEMERAL = 1 << 6 #You can use the EPHEMERAL message flag 1 << 6 (64) to send a message that only the user can see


def handle(body: bytes, signature: str, timestamp: str) -> tuple[int, dict[str, Any]]:
    if not verify(os.environ["DISCORD_PUBLIC_KEY"], body, signature, timestamp):
        return 401, {"error": "invalid request signature"}

    interaction = json.loads(body)
    if interaction["type"] == PING:
        return 200, {"type": PONG}
    if interaction["type"] == APPLICATION_COMMAND:
        return 200, reply(run_command(interaction))
    return 400, {"error": "unluggy"}


def run_command(interaction: dict[str, Any]) -> str:
    guild_id = interaction.get("guild_id")
    if not guild_id:
        return "This command only works in a server."

    data = interaction["data"]
    if data["name"] == "setchannel":
        channel_id = data["options"][0]["value"]
        store.set_channel(guild_id, channel_id)
        if start_posting():
            return f"MyFuture activities will be posted in <#{channel_id}> within a minute."
        return f"MyFuture activities will be posted in <#{channel_id}> at the next scheduled run."
    if data["name"] == "stop":
        store.remove_channel(guild_id)
        return "MyFuture activities will no longer be posted in this server."
    return f"Unknown command: {data['name']}"


def start_posting() -> bool:
    """Ask GitHub to run the posting workflow now. Returns whether it was started."""
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPO")
    if not token or not repo:
        return False
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/workflows/{POST_WORKFLOW}/dispatches",
        data=json.dumps({"ref": "main"}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "myfuture-discord-bot",
        },
    )
    try:
        # short timeout: Discord needs our reply within 3 seconds
        with urllib.request.urlopen(request, timeout=2):
            return True
    except OSError as error:  # includes HTTP errors and timeouts
        log.warning("Could not start the posting workflow: %s", error)
        return False


def reply(content: str) -> dict[str, Any]:
    return {"type": CHANNEL_MESSAGE, "data": {"content": content, "flags": EPHEMERAL}}


def verify(public_key: str, body: bytes, signature: str, timestamp: str) -> bool:
    try:
        VerifyKey(bytes.fromhex(public_key)).verify(
            timestamp.encode() + body, bytes.fromhex(signature)
        )
    except (BadSignatureError, ValueError):
        return False
    return True

HOME_PAGE = Path(__file__).with_name("home.html")


# Vercel function
class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send(200, "text/html; charset=utf-8", HOME_PAGE.read_bytes())

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        status, payload = handle(
            body,
            self.headers.get("X-Signature-Ed25519", ""),
            self.headers.get("X-Signature-Timestamp", ""),
        )
        self.send(status, "application/json", json.dumps(payload).encode())

    def send(self, status: int, content_type: str, data: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
