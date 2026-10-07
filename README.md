# MyFuture Discord bot

Posts new [TU/e MyFuture](https://myfuture.tue.nl) activities to a Discord channel: one
embed per activity 

## Usage
- You must have `Manage Server permission` for a server in order to use the bot
- Add the bot: [link](https://discord.com/oauth2/authorize?client_id=1555935047544995992&permissions=84992&integration_type=0&scope=bot+applications.commands)

 - Add the channel the bot should post in: `/setchannel #channel`
 - Wait a few seconds then the activities will show up
## Local Development

1. In the [Discord Developer Portal](https://discord.com/developers/applications), click
   **New Application**. Note the **Application ID** on the *General Information* page.
2. On the **Bot** page, click **Reset Token** and copy the token. No privileged intents
   are needed.
3. Invite the bot to your server 
4. In Discord, turn on **Developer Mode** (User Settings → Advanced), then right-click
   the channel the bot should post in and choose **Copy Channel ID**.

## Commands

 - Run the bot: `uv run bot`
 - Run test cases: `uv run pytest`
