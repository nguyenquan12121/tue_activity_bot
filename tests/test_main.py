from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.__main__ import discord_token, main


@pytest.fixture(autouse=True)
def no_dotenv():
    with patch("src.__main__.load_dotenv"):
        yield


def test_discord_token_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", " token ")
    assert discord_token() == "token"


def test_missing_token_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        discord_token()


def test_posts_to_every_saved_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    with (
        patch("src.__main__.store.get_channels", return_value={"1": "11", "2": "22"}),
        patch("src.__main__.fetch_activities", AsyncMock(return_value=[])),
        patch("src.__main__.post_new_activities", AsyncMock()) as post,
    ):
        assert main() == 0
    post.assert_awaited_once_with("token", [11, 22], [])