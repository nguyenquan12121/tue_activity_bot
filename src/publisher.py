from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence

import discord

from .scraper import Activity

log = logging.getLogger(__name__)

EMBED_COLOUR = discord.Color.from_str("#0000ff")
HISTORY_LIMIT = 200

async def post_new_activities(
    token: str, channel_ids: Iterable[int], activities: Sequence[Activity]
) -> None:
    discord.VoiceClient.warn_nacl = discord.VoiceClient.warn_dave = False  # quiet voice warnings
    async with discord.Client(intents=discord.Intents.default()) as client:
        await client.login(token)
        assert client.user is not None  # set by login()
        for channel_id in channel_ids:
            try:
                channel = await client.fetch_channel(channel_id)
                await publish_new(channel, client.user.id, activities)
            except (discord.NotFound, discord.Forbidden) as error:
                # channel deleted, or the bot was removed / lost permissions
                log.warning("Skipping channel %s: %s", channel_id, error)


async def publish_new(
    channel: discord.abc.Messageable, bot_user_id: int, activities: Sequence[Activity]
) -> list[Activity]:
    posted_urls = set()
    async for message in channel.history(limit=HISTORY_LIMIT):
        if message.author.id == bot_user_id:
            posted_urls.update(embed.url for embed in message.embeds if embed.url)

    new = [activity for activity in activities if activity.url not in posted_urls]
    log.info("%d of %d activities are new", len(new), len(activities))
    for activity in new:
        await channel.send(embed=build_embed(activity))
        log.info("Posted %s", activity.url)
    return new


def build_embed(activity: Activity) -> discord.Embed:
    embed = discord.Embed(
        title=activity.title,
        url=activity.url,
        colour=EMBED_COLOUR,
    )
    if activity.subtitle:
        embed.description = activity.subtitle
    if activity.when:
        embed.add_field(name="When", value=activity.when)
    if activity.image_url:
        embed.set_image(url=activity.image_url)
    embed.set_footer(text="MyFuture - TU/e")
    return embed
