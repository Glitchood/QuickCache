import discord

from io import BytesIO
from utils import default
from utils.default import CustomContext
from discord.ext import commands
from utils.data import DiscordBot

class Discord_Info(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx: CustomContext):
        """ Get all roles in current server """
        allroles = ""

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            allroles += f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r\n"

        data = BytesIO(allroles.encode("utf-8"))
        await ctx.send(content=f"Roles in **{ctx.guild.name}**", file=discord.File(data, filename=f"{default.timetext('Roles')}"))

async def setup(bot):
    await bot.add_cog(Discord_Info(bot))