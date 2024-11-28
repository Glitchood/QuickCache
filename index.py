import discord
from discord.ui import Select, View
from utils import config, data

config = config.Config.from_env(".env")
print("Logging in...")

bot = data.DiscordBot(
    config=config,
    command_prefix=config.discord_prefix,
    prefix=config.discord_prefix,
    command_attrs=dict(hidden=True),
    help_command=data.HelpFormat(),
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
    intents=discord.Intents(
        guilds=True,
        members=True,
        messages=True,
        reactions=True,
        presences=True,
        message_content=True,
    ),
)


@bot.event
async def on_ready():
    print("Ready!\n-------------------")


try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")
