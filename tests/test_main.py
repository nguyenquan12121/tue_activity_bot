from __future__ import annotations

import pytest

from src.__main__ import discord_settings


def test_discord_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", " token ")
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "123")
    assert discord_settings() == ("token", 123)
