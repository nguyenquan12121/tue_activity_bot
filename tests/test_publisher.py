from __future__ import annotations

from types import SimpleNamespace

from src.publisher import build_embed
from src.scraper import Activity

BOT_ID = 1
OTHER_ID = 2


def activity(n: int, **overrides) -> Activity:
    fields = {
        "url": f"https://myfuture.tue.nl/student/activity/{n}",
        "title": f"Activity {n}",
        "subtitle": "",
        "when": "",
        "image_url": None,
    }
    return Activity(**{**fields, **overrides})


def message(author_id: int, *urls: str) -> SimpleNamespace:
    return SimpleNamespace(
        author=SimpleNamespace(id=author_id),
        embeds=[SimpleNamespace(url=url) for url in urls],
    )

def test_build_embed_full() -> None:
    embed = build_embed(
        activity(1, subtitle="Sub", when="Tomorrow", image_url="https://example.com/x.png")
    )
    assert embed.title == "Activity 1"
    assert embed.description == "Sub"
    assert embed.fields[0].name == "When"
    assert embed.fields[0].value == "Tomorrow"
    assert embed.image.url == "https://example.com/x.png"


def test_build_embed_minimal() -> None:
    embed = build_embed(activity(1))
    assert embed.description is None
    assert embed.fields == []
    assert embed.image.url is None
