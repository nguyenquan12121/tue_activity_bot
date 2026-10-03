# MyFuture Discord bot

Posts new [TU/e MyFuture](https://myfuture.tue.nl) activities to a Discord channel: one
embed per activity 

## Setup

1. In the [Discord Developer Portal](https://discord.com/developers/applications), click
   **New Application**. Note the **Application ID** on the *General Information* page.
2. On the **Bot** page, click **Reset Token** and copy the token. No privileged intents
   are needed.
3. Invite the bot to your server 
4. In Discord, turn on **Developer Mode** (User Settings → Advanced), then right-click
   the channel the bot should post in and choose **Copy Channel ID**.

## Running the bot

```sh
uv run --env-file .env myfuture-bot
```
