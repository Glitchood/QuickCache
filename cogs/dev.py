import discord
from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from ui.manage import gen_cache_overview


class Development(commands.Cog):
    """DEVELOPMENT USE ONLY. DO NOT USE IN PUBLIC VERSION."""

    def __init__(self, bot):
        self.bot = bot

    def gen_cache_embeds(self, cacheList):
        embedList = []
        for cache in cacheList:
            guild = self.bot.get_guild(cache.get("guild_id"))
            if not guild:
                continue  # Skip if guild is not found

            categoryChannel = guild.get_channel(cache.get("category_id"))
            if not categoryChannel:
                continue  # Skip if category is not found

            cache_embed = gen_cache_overview(categoryChannel, cache.get("tags"))
            embedList.append(cache_embed)
        return embedList

    @commands.command()
    async def purge(self, ctx: CustomContext, num: int = 10):
        """Purges num messages in the current channel. If in DM, clears only bot's messages."""  # noqa E501
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
        num += 1
        if isinstance(ctx.channel, discord.DMChannel):

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

    @commands.command()
    async def close(self, ctx: CustomContext, num: int = 10):
        """Deletes all channels within a category and the category itself which starts with [QC]"""  # noqa E501

        # Fetch all categories that start with [QC]
        qc_categories = [
            category
            for category in ctx.guild.categories
            if category.name.startswith("[QC]")
        ]

        # Sort categories by creation date (optional)
        qc_categories = sorted(qc_categories, key=lambda c: c.created_at)

        # Limit to the number specified by `num`
        qc_categories = qc_categories[:num]

        if not qc_categories:
            await ctx.send("No categories starting with `[QC]` found.")
            return

        # Iterate over the categories and delete them
        for category in qc_categories:
            # Delete all channels within the category
            for channel in category.channels:
                await channel.delete()

            # Delete the category itself
            await category.delete()

        # Send a confirmation message
        await ctx.send(
            f"Deleted {len(qc_categories)} categories starting with `[QC]`.",
            delete_after=5,
        )

    @commands.command(aliases=["f"])
    async def fing(self, ctx: CustomContext):
        await ctx.send("Fong! `{0}`".format(round(self.bot.latency, 3)))


async def setup(bot: DiscordBot):
    await bot.add_cog(Development(bot))
