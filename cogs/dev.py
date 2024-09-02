import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

from utils.data import DiscordBot
from utils.default import CustomContext


class Development(commands.Cog):
    """DEVELOPMENT USE ONLY. DO NOT USE IN PUBLIC VERSION."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def purge(self, ctx: CustomContext, num: int = 10):
        """Purges num messages in the current channel. If in DM, clears only bot's messages."""
        if ctx.guild:
            # If in a server, check if the bot has permission to manage messages
            if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.send(
                    "I don't have permission to manage messages in this channel."
                )
                return

        # Ensure the number is within a reasonable range
        if num < 1 or num > 100:
            await ctx.send("You can only purge between 1 and 100 messages.")
            return

        if isinstance(ctx.channel, discord.DMChannel):
            # If in DM, filter and delete only the bot's messages
            def is_bot_message(msg):
                return msg.author == self.bot.user

            # Fetch the messages and filter
            messages = [
                msg
                async for msg in ctx.channel.history(limit=num)
                if is_bot_message(msg)
            ]
            for msg in messages:
                await msg.delete()
            await ctx.send(f"Deleted {len(messages)} bot messages.", delete_after=5)
        else:
            # Fetch and delete messages in a server channel
            deleted = await ctx.channel.purge(limit=num)
            await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)


async def setup(bot: DiscordBot):
    await bot.add_cog(Development(bot))
