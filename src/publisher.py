from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

import discord

from .scraper import Activity

log = logging.getLogger(__name__)

EMBED_COLOUR = discord.Color.from_str("#0000ff")
HISTORY_LIMIT = 200
#    Returns the servers that can never be posted to again: the channel was deleted or the bot was removed from the server.
async def post_new_activities(
    token: str, channels: Mapping[int, int], activities: Sequence[Activity]
) -> list[int]:
    discord.VoiceClient.warn_nacl = discord.VoiceClient.warn_dave = False  # quiet voice warnings
    gone = []
    async with discord.Client(intents=discord.Intents.default()) as client:
        await client.login(token)
        assert client.user is not None  # set by login()
        for guild_id, channel_id in channels.items():
            try:
                channel = await client.fetch_channel(channel_id)
                await publish_new(channel, client.user.id, activities)
            except discord.NotFound as error:
                log.warning("Channel %s was deleted: %s", channel_id, error)
                gone.append(guild_id)
            except discord.Forbidden as error:
                # same error whether the bot was kicked or only lacks permissions in the channel
                if await in_guild(client, guild_id):
                    log.warning("Skipping channel %s, missing permissions: %s", channel_id, error)
                else:
                    log.warning("Bot was removed from server %s", guild_id)
                    gone.append(guild_id)
    return gone


async def in_guild(client: discord.Client, guild_id: int) -> bool:
    try:
        await client.fetch_guild(guild_id)
    except (discord.NotFound, discord.Forbidden):
        return False
    return True


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
