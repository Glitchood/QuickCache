import discord
from discord.ext import commands

from utils.data import DiscordBot
from ui.manage import ManageCacheView


class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """Sets up a QuickCache in the current server"""
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.send("❌ I don't have permission to manage channels.")
            return

        # Send the initial message with the view
        view = ManageCacheView(bot=ctx.bot, user_id=ctx.author.id, cog=self)
        sent_message = await ctx.send(
            "### Click the button below to create a QuickCache.\n-# Or, load preferences from JSON",  # noqa E501
            view=view,
        )

        # Store the message_id for later deletion
        view.message_id = sent_message.id

    async def on_setup_finished(
        self,
        interaction: discord.Interaction,
        tags: list[str],
        category: discord.CategoryChannel,
    ):
        """Handle the final steps after the setup is finished."""
        # You can add any final actions here, such as SAVE to a database
        # cache_name = category.name[5::]
        # category_names = [channel.name for channel in category.channels]

        # embed = await generate_embed(cache_name, category_names, tags)

        # await interaction.response.send_message(embed=embed)


async def setup(bot: DiscordBot):
    await bot.add_cog(Manage(bot))
