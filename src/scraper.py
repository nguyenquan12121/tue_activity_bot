from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp

log = logging.getLogger(__name__)

EVERYONE_URL = "https://myfuture.tue.nl/everyone"
TIMEZONE = ZoneInfo("Europe/Amsterdam")

_CARD_COMPONENT = "tue.base-card"
_ACTIVITY_PATH = "/student/activity/"

@dataclass(frozen=True)
class Activity:
    url: str
    title: str
    subtitle: str
    when: str
    image_url: str | None


async def fetch_activities(*, now: datetime | None = None) -> list[Activity]:
    html = await download(EVERYONE_URL)
    return parse_activities(html, now=now or datetime.now(TIMEZONE))


def parse_activities(html: str, *, now: datetime) -> list[Activity]:
    collector = CardCollector()
    collector.feed(html)
    collector.close()
    activities = []
    for card in collector.cards:
        url = clean(card.get("href"))
        if _ACTIVITY_PATH not in url:
            continue  # other cards, such as alumni interviews
        when = clean(card.get("pretitle"))
        activities.append(
            Activity(
                url=url,
                title=clean(card.get("title")) or "MyFuture activity",
                subtitle=clean(card.get("subtitle")),
                when=when,
                image_url=clean(card.get("imageUrl")) or None,
            )
        )
    return activities

class CardCollector(HTMLParser):

    def __init__(self) -> None:
        super().__init__()
        self.cards: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "wire:initial-data" and value:
                state = json.loads(value)
                if state.get("fingerprint", {}).get("name") == _CARD_COMPONENT:
                    self.cards.append(state.get("serverMemo", {}).get("data", {}))


def clean(value: object) -> str:
    return " ".join(value.split()) if isinstance(value, str) else ""


async def download(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    raise AssertionError("unreachable")
