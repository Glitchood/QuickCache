from discord.ext import commands

from utils.data import DiscordBot


class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """Sets up a QuickCache"""
        sent_message = await ctx.send(
            "### Click the button below to create a QuickCache.\n-# Or, load preferences from JSON"  # noqa E501
        )


async def setup(bot: DiscordBot):
    await bot.add_cog(Manage(bot))
