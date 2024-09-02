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
        # kwargs found at https://docs.pycord.dev/en/master/api.html?highlight=discord%20intents#discord.Intents
        guilds=True,
        members=True,
        messages=True,
        reactions=True,
        presences=True,
        message_content=True,
    ),
)

# The category ID where the channels are located
CATEGORY_ID = 1279645963820204042
GUILD_ID = 1279591002512031836


class CategorySelect(Select):
    def __init__(self, guild, message_id, options, message_content):
        super().__init__(
            placeholder="Choose a channel...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.guild = guild
        self.message_id = message_id  # Ensure this is set correctly
        self.message_content = message_content

    async def callback(self, interaction: discord.Interaction):
        # Get the selected channel ID
        channel_id = int(self.values[0])
        # Fetch the channel using the ID from the stored guild context
        channel = self.guild.get_channel(channel_id)
        if channel:
            # Send the message content to the selected channel
            await channel.send(self.message_content)
            # Send a confirmation message
            await interaction.response.send_message(
                f"Message sent to {channel.mention}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Failed to send the message. The channel may no longer exist.",
                ephemeral=True,
            )

        # Delete the original dropdown message
        try:
            original_message = await interaction.channel.fetch_message(self.message_id)
            await original_message.delete()
        except discord.NotFound:
            pass  # Message already deleted or not found


async def save_snippet(message):
    # Fetch the guild that contains the category
    guild = bot.get_guild(GUILD_ID)

    if guild:
        # Fetch the category channel from the guild
        category = guild.get_channel(CATEGORY_ID)

        if category and isinstance(category, discord.CategoryChannel):
            # Create options for the Select dropdown
            options = [
                discord.SelectOption(label=channel.name, value=str(channel.id))
                for channel in category.text_channels
            ]

            if options:
                # Create the dropdown menu with the guild context
                select = CategorySelect(
                    guild=guild,
                    message_id=message.id,  # Pass the message ID for deletion later
                    options=options,
                    message_content=message.content,
                )
                view = View()
                view.add_item(select)

                # Send the dropdown menu to the user in DMs
                dropdown_message = await message.channel.send(
                    "Select a category to save the snippet:", view=view
                )

                # Update the ChannelSelect instance with the correct message ID
                select.message_id = dropdown_message.id
            else:
                await message.channel.send(
                    "No channels found in the specified category."
                )
        else:
            await message.channel.send("The specified category does not exist.")
    else:
        await message.channel.send("The specified guild does not exist.")


@bot.event
async def on_ready():
    print(f"Ready!\n-------------------")


@bot.event
async def on_message(message):
    # Check if the message is a direct message (DM) and not sent by the bot itself
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        # Respond with the exact same message
        if message.content.startswith(bot.command_prefix) and not message.author.bot:
            await bot.process_commands(message)
        else:
            await save_snippet(message)
    else:
        # Process commands if the message was not a DM or if other bot logic is needed
        await bot.process_commands(message)


try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")
