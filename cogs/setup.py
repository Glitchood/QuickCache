import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

from utils.data import DiscordBot
from utils.default import CustomContext

class RemoveChannelModal(Modal):
    def __init__(self, *, bot, category, **kwargs):
        super().__init__(title='Remove a Category from QuickCache', **kwargs)
        self.bot = bot
        self.category = category

        # Add a text input to the modal for the channel name
        self.channel_name = TextInput(
            label='Category Name',
            placeholder='Enter the name of the CHANNEL to remove...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.channel_name.value
        channel = discord.utils.get(self.category.channels, name=channel_name)

        if channel:
            await channel.delete()
            await interaction.response.send_message(f"Category `{channel_name}` removed from `{self.category.name}`.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No channel named `{channel_name}` found in `{self.category.name}`.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)

class RenameChannelModal(Modal):
    def __init__(self, *, bot, category, **kwargs):
        super().__init__(title='Rename a Category in QuickCache', **kwargs)
        self.bot = bot
        self.category = category

        # Add a text input to the modal for the current channel name
        self.current_channel_name = TextInput(
            label='Current Category Name',
            placeholder='Enter the current name of the CHANNEL...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.current_channel_name)

        # Add a text input to the modal for the new channel name
        self.new_channel_name = TextInput(
            label='New Category Name',
            placeholder='Enter the new name for the category...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.new_channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        current_channel_name = self.current_channel_name.value
        new_channel_name = self.new_channel_name.value

        # Find the channel in the category
        channel = discord.utils.get(self.category.channels, name=current_channel_name)

        if channel:
            await channel.edit(name=new_channel_name)
            await interaction.response.send_message(f"Category `{current_channel_name}` renamed to `{new_channel_name}`.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No channel named `{current_channel_name}` found in `{self.category.name}`.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)

class AddChannelModal(Modal):
    def __init__(self, *, bot, category, **kwargs):
        super().__init__(title='Add a Category to QuickCache', **kwargs)
        self.bot = bot
        self.category = category

        # Add a text input to the modal for the channel name
        self.channel_name = TextInput(
            label='Category Name',
            placeholder='Enter the name for the new category...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.channel_name.value
        await self.category.create_text_channel(name=channel_name)
        await interaction.response.send_message(f"Category `{channel_name}` added to `{self.category.name}`.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)

class ManageChannelsView(View):
    def __init__(self, *, bot, user_id, category, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.user_id = user_id
        self.category = category

    @discord.ui.button(emoji="➕", label="Add", style=discord.ButtonStyle.success)
    async def add_channel_button(self, interaction: discord.Interaction, button: Button):
        # Check if the user who clicked the button is the same as the one who invoked the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return
        # Respond to the interaction with a modal to add a channel
        await interaction.response.send_modal(AddChannelModal(bot=self.bot, category=self.category))

    @discord.ui.button(emoji="➖", label="Delete", style=discord.ButtonStyle.danger)
    async def remove_channel_button(self, interaction: discord.Interaction, button: Button):
        # Check if the user who clicked the button is the same as the one who invoked the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return
        # Respond to the interaction with a modal to remove a channel
        await interaction.response.send_modal(RemoveChannelModal(bot=self.bot, category=self.category))

    @discord.ui.button(emoji="✏️", label="Rename", style=discord.ButtonStyle.gray)
    async def rename_channel_button(self, interaction: discord.Interaction, button: Button):
        # Check if the user who clicked the button is the same as the one who invoked the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return
        # Respond to the interaction with a modal to rename a channel
        await interaction.response.send_modal(RenameChannelModal(bot=self.bot, category=self.category))

    @discord.ui.button(emoji="☑️", label="Confirm", style=discord.ButtonStyle.primary)
    async def confirm_channel_button(self, interaction: discord.Interaction, button: Button):
        # Check if the user who clicked the button is the same as the one who invoked the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return

        # Initialize the ManageTagsView with an empty list of tags
        view = ManageTagsView(bot=self.bot, user_id=self.user_id, tags=[])

        # Send an ephemeral message with the ManageTagsView
        await interaction.response.send_message(f"Manage **tags** in `{cache_name}`::", view=view, ephemeral=True)


class AddTagModal(Modal):
    def __init__(self, *, bot, user_id, tags, **kwargs):
        super().__init__(title='Add Tag', **kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags

        self.tag_input = TextInput(
            label='Tag',
            placeholder='Enter a tag...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.tag_input)

    async def on_submit(self, interaction: discord.Interaction):
        tag = self.tag_input.value

        if tag not in self.tags:
            self.tags.append(tag)
            await interaction.response.send_message(f"Tag `{tag}` added.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Tag `{tag}` already exists.", ephemeral=True)

class RemoveTagModal(Modal):
    def __init__(self, *, bot, user_id, tags, **kwargs):
        super().__init__(title='Remove Tag', **kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags

        self.tag_input = TextInput(
            label='Tag',
            placeholder='Enter the tag to remove...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.tag_input)

    async def on_submit(self, interaction: discord.Interaction):
        tag = self.tag_input.value

        if tag in self.tags:
            self.tags.remove(tag)
            await interaction.response.send_message(f"Tag `{tag}` removed.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No such tag `{tag}` found.", ephemeral=True)

class RenameTagModal(Modal):
    def __init__(self, *, bot, user_id, tags, **kwargs):
        super().__init__(title='Rename Tag', **kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags

        self.current_tag_input = TextInput(
            label='Current Tag',
            placeholder='Enter the current tag name...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.new_tag_input = TextInput(
            label='New Tag',
            placeholder='Enter the new tag name...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.current_tag_input)
        self.add_item(self.new_tag_input)

    async def on_submit(self, interaction: discord.Interaction):
        current_tag = self.current_tag_name.value
        new_tag = self.new_tag_name.value

        if current_tag not in self.tags:
            await interaction.response.send_message(f"No tag named `{current_tag}` found.", ephemeral=True)
            return

        if new_tag in self.tags:
            await interaction.response.send_message("A tag with this name already exists. Please choose a different name.", ephemeral=True)
            return

        self.tags[self.tags.index(current_tag)] = new_tag
        await interaction.response.send_message(f"Tag `{current_tag}` renamed to `{new_tag}`.", ephemeral=True)

class ManageTagsView(View):
    def __init__(self, *, bot, user_id, tags, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.user_id = user_id
        self.tags = tags  # List of tags collected from the user

    @discord.ui.button(emoji="➕", label="Add", style=discord.ButtonStyle.success)
    async def add_tag_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return
        await interaction.response.send_modal(AddTagModal(bot=self.bot, user_id=self.user_id, tags=self.tags))

    @discord.ui.button(emoji="➖", label="Delete", style=discord.ButtonStyle.danger)
    async def remove_tag_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return
        await interaction.response.send_modal(RemoveTagModal(bot=self.bot, user_id=self.user_id, tags=self.tags))

    @discord.ui.button(emoji="✏️",label="Rename", style=discord.ButtonStyle.blurple)
    async def rename_tag_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return
        await interaction.response.send_modal(RenameTagModal(bot=self.bot, user_id=self.user_id, tags=self.tags))

    @discord.ui.button(emoji="☑️", label="Confirm", style=discord.ButtonStyle.primary)
    async def confirm_tags_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return

        # Show the final list of tags
        if not self.tags:
            tags_summary = "No tags have been added."
        else:
            tags_summary = '\n'.join(self.tags)

        await interaction.response.send_message(f"Tags confirmed:\n{tags_summary}", ephemeral=True)


class SetupCacheModal(Modal):
    def __init__(self, *, bot, user_id, **kwargs):
        super().__init__(title='Setup a new QuickCache', **kwargs)
        self.bot = bot
        self.user_id = user_id

        # Add a text input to the modal
        self.cache_name = TextInput(
            label='Cache Name',
            placeholder='Enter the name for the cache...',
            required=True,
            min_length=1,
            max_length=40,
        )
        self.add_item(self.cache_name)

    async def on_submit(self, interaction: discord.Interaction):
        cache_name = self.cache_name.value
        category_name = f"[QC] {cache_name}"

        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("I don't have permission to manage channels.", ephemeral=True)
            return

        category = await interaction.guild.create_category(category_name)
        await interaction.response.send_message(f"Cache `{cache_name}` setup successfully!", ephemeral=True)

        # Send a follow-up message with options to add or remove channels
        view = ManageChannelsView(bot=self.bot, user_id=self.user_id, category=category)
        await interaction.followup.send(f"Manage **categories** in `{cache_name}`:", view=view, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)

class SetupCacheView(View):
    def __init__(self, *, bot, user_id, message_id=None, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.user_id = user_id
        self.message_id = message_id  # Store the message_id to delete it later

    @discord.ui.button(label="Setup QuickCache", style=discord.ButtonStyle.primary)
    async def setup_button(self, interaction: discord.Interaction, button: Button):
        # Check if the user who clicked the button is the same as the one who invoked the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
            return

        # Respond to the interaction with the modal
        await interaction.response.send_modal(SetupCacheModal(bot=self.bot, user_id=self.user_id))

        # Attempt to delete the original message after responding
        if self.message_id:
            try:
                original_message = await interaction.channel.fetch_message(self.message_id)
                await original_message.delete()
            except discord.NotFound:
                pass  # Message already deleted or not found

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """ Sets up a QuickCache in the current server """
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.send("I don't have permission to manage channels.")
            return

        # Send the initial message with the view
        view = SetupCacheView(bot=ctx.bot, user_id=ctx.author.id)
        sent_message = await ctx.send("Click the button below to create a QuickCache.", view=view, delete_after=120)
        
        # Store the message_id for later deletion
        view.message_id = sent_message.id

async def setup(bot: DiscordBot):
    await bot.add_cog(Setup(bot))
