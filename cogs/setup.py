import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

from utils.data import DiscordBot
from ui.setup.src import ManageCacheView


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """Sets up a QuickCache in the current server"""
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.send("✖️ I don't have permission to manage channels.")
            return

        # Send the initial message with the view
        view = ManageCacheView(bot=ctx.bot, user_id=ctx.author.id)
        sent_message = await ctx.send(
            "Click the button below to create a QuickCache.",
            view=view,
            delete_after=120,
        )

        # Store the message_id for later deletion
        view.message_id = sent_message.id


async def setup(bot: DiscordBot):
    await bot.add_cog(Setup(bot))
