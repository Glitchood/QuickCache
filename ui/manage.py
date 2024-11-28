import discord
from datetime import datetime


def gen_cache_overview(category: discord.CategoryChannel, tag_list):
    """Generates a Embed object using CategoryChannel and list of tags"""

    cache_name = category.name.removeprefix("[QC] ")
    category_list = [channel.name for channel in category.channels]

    embed = discord.Embed(
        title=f"{cache_name}", colour=0xF0D464, timestamp=datetime.now()
    )

    if category_list:
        categories = "```\n" + "\n".join(category_list) + "\n```"
        embed.add_field(
            name="**__Categories:__**",
            value=categories,
            inline=False,
        )
    else:
        embed.add_field(
            name="**__Categories:__ None**",
            value="",
            inline=False,
        )

    # Handle the first three unique fields if present
    if len(tag_list) > 0:
        embed.add_field(name="**__Tags:__**", value=f"`{tag_list[0]}`", inline=True)
    else:
        embed.add_field(name="**__Tags:__ None**", value="‍", inline=True)
    if len(tag_list) > 1:
        embed.add_field(name="‍", value=f"`{tag_list[1]}`", inline=True)
    if len(tag_list) > 2:
        embed.add_field(name="‍", value=f"`{tag_list[2]}`", inline=True)
    # Handle the remaining fields with default formatting
    for index in range(3, len(tag_list)):
        embed.add_field(name="", value=f"`{tag_list[index]}`", inline=True)

    embed.set_thumbnail(
        url="https://cdn-0.emojis.wiki/emoji-pics/microsoft/card-index-dividers-microsoft.png"  # noqa E501
    )

    embed.set_footer(
        text="QuickCache",
        icon_url="https://cdn-0.emojis.wiki/emoji-pics/microsoft/card-file-box-microsoft.png",  # noqa E501
    )

    return embed
