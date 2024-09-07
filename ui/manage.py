import discord
from datetime import datetime
from discord.ui import Modal, TextInput, View, Button
import json
import io


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


class ManageChannelsView(View):
    def __init__(self, *, bot, user_id, category, cog, **kwargs):
        super().__init__(timeout=300, **kwargs)  # 5 minutes timeout
        self.bot = bot
        self.user_id = user_id
        self.category = category
        self.cog = cog  # Reference to the Setup cog
        self.tags = []  # Initialize an empty list of tags

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You are not authorized to use this button.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        # This method will be called when the view times out (after 5 minutes)
        for channel in self.category.channels:
            await channel.delete()
        await self.category.delete()

    @discord.ui.button(emoji="➕", label="Add", style=discord.ButtonStyle.success)
    async def add_channel_button(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.send_modal(
            AddChannelModal(bot=self.bot, category=self.category)
        )

    @discord.ui.button(emoji="➖", label="Delete", style=discord.ButtonStyle.danger)
    async def remove_channel_button(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.send_modal(
            RemoveChannelModal(bot=self.bot, category=self.category)
        )

    @discord.ui.button(emoji="✏️", label="Rename", style=discord.ButtonStyle.gray)
    async def rename_channel_button(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.send_modal(
            RenameChannelModal(bot=self.bot, category=self.category)
        )

    @discord.ui.button(emoji="☑️", label="Confirm", style=discord.ButtonStyle.primary)
    async def confirm_channel_button(
        self, interaction: discord.Interaction, button: Button
    ):
        view = ManageTagsView(
            bot=self.bot,
            user_id=self.user_id,
            tags=self.tags,
            cog=self.cog,
            category=self.category,
        )
        await interaction.response.edit_message(
            content="**Manage __tags__**:",
            embed=gen_cache_overview(self.category, self.tags),
            view=view,
        )
        self.stop()


class ManageTagsView(View):
    def __init__(self, *, bot, user_id, tags, cog, category, **kwargs):
        super().__init__(timeout=300, **kwargs)  # 5 minutes timeout
        self.bot = bot
        self.user_id = user_id
        self.tags = tags
        self.cog = cog  # Reference to the Setup cog
        self.category = category

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You are not authorized to use this button.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        # This method will be called when the view times out (after 5 minutes)
        self.tags.clear()

    @discord.ui.button(emoji="➕", label="Add", style=discord.ButtonStyle.success)
    async def add_tag_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(
            AddTagModal(
                bot=self.bot,
                user_id=self.user_id,
                category=self.category,
                tags=self.tags,
            )
        )

    @discord.ui.button(emoji="➖", label="Remove", style=discord.ButtonStyle.danger)
    async def remove_tag_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(
            RemoveTagModal(
                bot=self.bot,
                user_id=self.user_id,
                category=self.category,
                tags=self.tags,
            )
        )

    @discord.ui.button(emoji="✏️", label="Rename", style=discord.ButtonStyle.gray)
    async def rename_tag_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(
            RenameTagModal(
                bot=self.bot,
                user_id=self.user_id,
                category=self.category,
                tags=self.tags,
            )
        )

    @discord.ui.button(
        emoji="☑️", label="Finish Setup", style=discord.ButtonStyle.primary
    )
    async def finish_tag_button(self, interaction: discord.Interaction, button: Button):

        view = SaveJSONView(
            bot=self.bot, user_id=self.user_id, category=self.category, tags=self.tags
        )
        cache_name = self.category.name.removeprefix("[QC] ")
        await interaction.response.edit_message(
            content=f"**`{cache_name}` Setup finished!**:",
            embed=gen_cache_overview(self.category, self.tags),
            view=view,
        )
        self.stop()


class ManageCacheView(View):
    def __init__(self, *, bot, user_id, cog, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.user_id = user_id
        self.cog = cog  # Reference to the Setup cog

    @discord.ui.button(label="Setup QuickCache", style=discord.ButtonStyle.primary)
    async def setup_button(self, interaction: discord.Interaction, button: Button):
        # Check if the user who clicked the button is the one who invoked the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You are not authorized to use this button.", ephemeral=True
            )
            return

        # Respond to the interaction with the modal
        await interaction.response.send_modal(
            ManageCacheModal(bot=self.bot, user_id=self.user_id, cog=self.cog)
        )

    @discord.ui.button(label="Load JSON", style=discord.ButtonStyle.secondary)
    async def load_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You are not authorized to use this button.", ephemeral=True
            )
            return

        # Respond to the interaction with the modal
        await interaction.response.send_modal(
            LoadJSONModal(bot=self.bot, user_id=self.user_id, cog=self.cog)
        )


class SaveJSONView(View):
    def __init__(
        self, *, bot, user_id, category: discord.CategoryChannel, tags, **kwargs
    ):
        super().__init__(**kwargs)
        self.bot = bot
        self.user_id = user_id
        self.category = category
        self.tags = tags

    @discord.ui.button(
        label="Save preferences as JSON", style=discord.ButtonStyle.secondary
    )
    async def save_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You are not authorized to use this button.", ephemeral=True
            )
            return

        cache_name = self.category.name.removeprefix("[QC] ")
        # Build the JSON structure
        quickcache_data = {
            "Cache_Name": cache_name,
            "Categories": [],
            "Tags": self.tags,
        }

        # Add channels to the JSON structure
        for channel in self.category.text_channels:
            quickcache_data["Categories"].append({"Category_name": channel.name})

        # Convert the data to a JSON string
        json_data = json.dumps(quickcache_data, indent=4)

        # Create a file-like object to send as a file
        json_file = io.StringIO(json_data)
        cache_name = self.category.name.removeprefix("[QC] ")
        json_file.name = f"{cache_name}_QuickCache.json"  # Give the file a name

        # Respond with the JSON file
        await interaction.response.send_message(
            content="Here's your QuickCache JSON file:",
            file=discord.File(json_file, filename=json_file.name),
            ephemeral=True,
        )


class LoadJSONModal(Modal):
    def __init__(self, *, bot, user_id, cog, **kwargs):
        super().__init__(title="Setup a new QuickCache", **kwargs)
        self.bot = bot
        self.user_id = user_id

        # Add a text input to the modal
        self.json_input = TextInput(
            label="Load JSON",
            placeholder="Paste JSON preferences for the cache...",
            required=True,
            min_length=1,
            style=discord.TextStyle.long,
        )
        self.add_item(self.json_input)
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        # Parse the JSON input
        try:
            cache_data = json.loads(self.json_input.value)
        except json.JSONDecodeError:
            await interaction.response.send_message(
                "❌ Invalid JSON format. Please try again.", ephemeral=True
            )
            return

        # Extract data from JSON
        cache_name = cache_data.get("Cache_Name", "Unnamed Cache")
        categories = cache_data.get("Categories", [])
        tags = cache_data.get("Tags", [])

        # Create a new category named "[QC] {Cache_Name}" in the guild
        guild = interaction.guild
        category_channel = await guild.create_category(f"[QC] {cache_name}")

        # Create channels within the newly created category
        created_channels = []
        for category in categories:
            channel_name = category.get("Channel_name", "Unnamed Channel")
            channel = await guild.create_text_channel(
                channel_name, category=category_channel
            )
            created_channels.append(channel)

        # Send a message with the setup confirmation
        view = SaveJSONView(
            bot=self.bot, user_id=self.user_id, category=category_channel, tags=tags
        )
        cache_name = category_channel.name.removeprefix("[QC] ")
        await interaction.response.edit_message(
            content=f"**`{cache_name}` Setup finished!**:",
            embed=gen_cache_overview(category_channel, tags),
            view=view,
        )


class AddTagModal(Modal):
    def __init__(self, *, bot, user_id, category, tags, **kwargs):
        super().__init__(title="Add Tag", **kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags
        self.category = category

        self.tag_input = TextInput(
            label="Tag",
            placeholder="Enter a tag...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.tag_input)

    async def on_submit(self, interaction: discord.Interaction):
        tag = self.tag_input.value

        if tag not in self.tags:
            self.tags.append(tag)
            await interaction.response.edit_message(
                content="**Manage __tags__**:",
                embed=gen_cache_overview(self.category, self.tags),
            )
        else:
            await interaction.response.send_message(
                f"❌ Tag `{tag}` already exists.", ephemeral=True
            )


class RemoveTagModal(Modal):
    def __init__(self, *, bot, user_id, category, tags, **kwargs):
        super().__init__(title="Add Tag", **kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags
        self.category = category

        self.tag_input = TextInput(
            label="Tag",
            placeholder="Enter the tag to remove...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.tag_input)

    async def on_submit(self, interaction: discord.Interaction):
        tag = self.tag_input.value

        if tag in self.tags:
            self.tags.remove(tag)
            await interaction.response.edit_message(
                content="**Manage __tags__**:",
                embed=gen_cache_overview(self.category, self.tags),
            )
        else:
            await interaction.response.send_message(
                f"❌ No such tag `{tag}` found.", ephemeral=True
            )


class RenameTagModal(Modal):
    def __init__(self, *, bot, user_id, category, tags, **kwargs):
        super().__init__(title="Add Tag", **kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags
        self.category = category

        self.current_tag_input = TextInput(
            label="Current Tag",
            placeholder="Enter the current tag name...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.new_tag_input = TextInput(
            label="New Tag",
            placeholder="Enter the new tag name...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.current_tag_input)
        self.add_item(self.new_tag_input)

    async def on_submit(self, interaction: discord.Interaction):
        current_tag = self.current_tag_input.value
        new_tag = self.new_tag_input.value

        if current_tag not in self.tags:
            await interaction.response.send_message(
                f"❌ No tag named `{current_tag}` found.", ephemeral=True
            )
            return

        if new_tag in self.tags:
            await interaction.response.send_message(
                f"❌ Tag `{new_tag}` already exists.",
                ephemeral=True,
            )
            return

        self.tags[self.tags.index(current_tag)] = new_tag
        await interaction.response.edit_message(
            content="**Manage __tags__**:",
            embed=gen_cache_overview(self.category, self.tags),
        )


class RemoveChannelModal(Modal):
    def __init__(self, *, bot, category, **kwargs):
        super().__init__(title="Remove a Category from QuickCache", **kwargs)
        self.bot = bot
        self.category = category

        self.channel_name = TextInput(
            label="Category Name",
            placeholder="Enter the name of the CHANNEL to remove...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.channel_name.value
        channel_name.lower()
        channel_name = channel_name.replace(" ", "-")
        channel = discord.utils.get(self.category.channels, name=channel_name)

        if channel:
            await channel.delete()
            await interaction.response.edit_message(
                content="**Manage __categories__**:",
                embed=gen_cache_overview(self.category, []),
            )

        else:
            await interaction.response.send_message(
                f"❌ No channel named `{channel_name}` found in `{self.category.name}`.",
                ephemeral=True,
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        import traceback

        # Use followup.send only if the interaction has already been responded to
        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )

        # Log the error for debugging purposes
        traceback.print_exception(type(error), error, error.__traceback__)


class RenameChannelModal(Modal):
    def __init__(self, *, bot, category, **kwargs):
        super().__init__(title="Rename a Category in QuickCache", **kwargs)
        self.bot = bot
        self.category = category

        self.current_channel_name = TextInput(
            label="Current Category Name",
            placeholder="Enter the current name of the CHANNEL...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.current_channel_name)

        self.new_channel_name = TextInput(
            label="New Category Name",
            placeholder="Enter the new name for the category...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.new_channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        current_channel_name = self.current_channel_name.value
        current_channel_name.lower()
        current_channel_name = current_channel_name.replace(" ", "-")
        new_channel_name = self.new_channel_name.value

        channel = discord.utils.get(self.category.channels, name=current_channel_name)

        new_channel = discord.utils.get(self.category.channels, name=new_channel_name)

        if channel:
            if not new_channel:
                await channel.edit(name=new_channel_name)
                await interaction.response.edit_message(
                    content="**Manage __categories__**:",
                    embed=gen_cache_overview(self.category, []),
                )
            else:
                await interaction.response.send_message(
                    f"❌ Category `{new_channel_name}` already exists.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                f"❌ No channel named `{current_channel_name}` found in `{self.category.name}`.",  # noqa E501
                ephemeral=True,
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        import traceback

        # Use followup.send only if the interaction has already been responded to
        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )

        # Log the error for debugging purposes
        traceback.print_exception(type(error), error, error.__traceback__)


class AddChannelModal(Modal):
    def __init__(self, *, bot, category, **kwargs):
        super().__init__(title="Add a Category to QuickCache", **kwargs)
        self.bot = bot
        self.category = category

        self.channel_name = TextInput(
            label="Category Name",
            placeholder="Enter the name for the new category...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.channel_name.value

        channel = discord.utils.get(self.category.channels, name=channel_name)

        if channel:
            await interaction.response.send_message(
                f"❌ Category `{channel_name}` already exists.",
                ephemeral=True,
            )
        else:
            await self.category.create_text_channel(name=channel_name)
            await interaction.response.edit_message(
                content="**Manage __categories__**:",
                embed=gen_cache_overview(self.category, []),
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        import traceback

        # Use followup.send only if the interaction has already been responded to
        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )

        # Log the error for debugging purposes
        traceback.print_exception(type(error), error, error.__traceback__)


class ManageCacheModal(Modal):
    def __init__(self, *, bot, user_id, cog, **kwargs):
        super().__init__(title="Setup a new QuickCache", **kwargs)
        self.bot = bot
        self.user_id = user_id

        # Add a text input to the modal
        self.cache_name = TextInput(
            label="Cache Name",
            placeholder="Enter the name for the cache...",
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.cache_name)
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        cache_name = self.cache_name.value
        category_name = f"[QC] {cache_name}"

        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "❌ I don't have permission to manage channels.", ephemeral=True
            )
            return

        category = await interaction.guild.create_category(category_name)

        # Send a follow-up message with options to add or remove channels
        view = ManageChannelsView(
            bot=self.bot, user_id=self.user_id, category=category, cog=self.cog
        )
        await interaction.response.edit_message(
            content="**Manage __categories__**:",
            embed=gen_cache_overview(category, []),
            view=view,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        import traceback

        # Use followup.send only if the interaction has already been responded to
        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "❌ Oops! Something went wrong while processing your request.",
                ephemeral=True,
            )

        # Log the error for debugging purposes
        traceback.print_exception(type(error), error, error.__traceback__)
