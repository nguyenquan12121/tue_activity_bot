from __future__ import annotations

import asyncio
import html
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.scraper import TIMEZONE, Activity, clean, fetch_activities, parse_activities

NOW = datetime(2026, 10, 3, 12, 0, tzinfo=TIMEZONE)


def card(data: dict, component: str = "tue.base-card") -> str:
    state = {"fingerprint": {"name": component}, "serverMemo": {"data": data}}
    return f'<div wire:initial-data="{html.escape(json.dumps(state), quote=True)}"></div>'


ACTIVITY_CARD = card(
    {
        "href": "https://myfuture.tue.nl/student/activity/123",
        "title": "  Career   Fair ",
        "subtitle": "Meet employers",
        "pretitle": "12 Oct 2026",
        "imageUrl": "https://example.com/fair.png",
    }
)


def test_parses_activity_card() -> None:
    assert parse_activities(ACTIVITY_CARD, now=NOW) == [
        Activity(
            url="https://myfuture.tue.nl/student/activity/123",
            title="Career Fair",
            subtitle="Meet employers",
            when="12 Oct 2026",
            image_url="https://example.com/fair.png",
        )
    ]


def test_skips_non_activity_cards() -> None:
    page = card({"href": "https://myfuture.tue.nl/alumni/interview/1", "title": "Alumni"})
    assert parse_activities(page, now=NOW) == []


def test_skips_other_components() -> None:
    page = card({"href": "https://myfuture.tue.nl/student/activity/1"}, component="tue.other")
    assert parse_activities(page, now=NOW) == []


def test_missing_fields_get_defaults() -> None:
    page = card({"href": "https://myfuture.tue.nl/student/activity/9"})
    [activity] = parse_activities(page, now=NOW)
    assert activity.title == "MyFuture activity"
    assert activity.subtitle == ""
    assert activity.when == ""
    assert activity.image_url is None


def test_clean() -> None:
    assert clean("  a \n b  ") == "a b"
    assert clean(None) == ""
    assert clean(42) == ""


def test_fetch_activities_uses_downloaded_page() -> None:
    with patch("src.scraper.download", AsyncMock(return_value=ACTIVITY_CARD)) as download:
        activities = asyncio.run(fetch_activities(now=NOW))
    download.assert_awaited_once()
    assert [a.title for a in activities] == ["Career Fair"]
