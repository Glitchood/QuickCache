import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime

from utils.data import DiscordBot
from ui.setup.src import ManageCacheView


async def generate_overview(tags, category):
    embed = discord.Embed(
        title="<quickcache_name>", colour=0x00B0F4, timestamp=datetime.now()
    )

    embed.add_field(
        name="**__Categories:__**",
        value="```\ncategory-1\ncategory-2\ncategory-3\ncategory-4\n```",
        inline=False,
    )
    embed.add_field(name="**__Tags:__**", value="`✨ tag`", inline=True)
    embed.add_field(name="‍", value="`🆕 tag_2`", inline=True)
    embed.add_field(name="‍", value="`✏️ tag_3`", inline=True)
    embed.add_field(name="", value="`tag_4`", inline=True)

    embed.set_thumbnail(
        url="https://cdn-0.emojis.wiki/emoji-pics/microsoft/card-index-dividers-microsoft.png"  # noqa E501
    )

    embed.set_footer(
        text="QuickCache",
        icon_url="https://cdn-0.emojis.wiki/emoji-pics/microsoft/card-file-box-microsoft.png",  # noqa E501
    )
    return embed


class Setup(commands.Cog):
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
            "Click the button below to create a QuickCache.",
            view=view,
            delete_after=120,
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
        # You can add any final actions here, such as saving to a database
        embed = await generate_overview(tags, category)
        await interaction.response.send_message(embed=embed)


async def setup(bot: DiscordBot):
    await bot.add_cog(Setup(bot))
