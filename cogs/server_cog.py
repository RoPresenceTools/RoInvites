import discord
from discord import app_commands
from discord.ext import commands
from styling.ri_colors import *

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__()
        self.label = "Go back"
        self.style = discord.ButtonStyle.secondary
        self.callback = self.back_button_callback

    async def back_button_callback(self, interaction: discord.Interaction):
        main_menu_view = SetupView()
        main_menu_embed = await main_menu_view.get_embed()
        await interaction.response.edit_message(
            embed=main_menu_embed,
            view=main_menu_view
        )

class SuccessView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.go_back = BackButton()
        self.add_item(self.go_back)

    async def on_timeout(self):
        self.go_back.disabled = True
        self.stop()

    async def get_embed(self, description):
        embed = discord.Embed(
            title="Success",
            description=description,
            color=green
        )
        return embed

class FailureView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.go_back = BackButton()
        self.add_item(self.go_back)

    async def on_timeout(self):
        self.go_back.disabled = True
        self.stop()

    async def get_embed(self, description):
        embed = discord.Embed(
            title="Failed",
            description=description,
            color=red
        )
        return embed

class ChannelView(discord.ui.View):
    def __init__(self, channel_type):
        super().__init__()
        self.result = None
        self.go_back = BackButton()
        self.channel_type = channel_type
        self.new_channel_name = "roinvites" if self.channel_type == "invite" else "announcements"

        self.channel_select = discord.ui.ChannelSelect(
            placeholder="Choose a channel...",
        )
        async def select_callback(interaction: discord.Interaction):
            self.result = self.channel_select.values[0]
            await interaction.response.defer()
            self.stop()

        self.create_channel_button = discord.ui.Button(
            label="Create Channel",
            style=discord.ButtonStyle.primary
        )

        async def button_callback(interaction: discord.Interaction):
            if not interaction.guild.me.guild_permissions.manage_channels:
                failure_view = FailureView()
                await interaction.response.edit_message(
                    embed=await failure_view.get_embed("A server admin must enable the **Manage Channels** permission to create new channels."),
                    view=failure_view
                )

            channel = await interaction.guild.create_text_channel(self.new_channel_name)
            success = await interaction.client.settings_manager.set_channel(interaction.guild, self.channel_type, channel)
            if success == True:
                success_view = SuccessView()
                await interaction.response.edit_message(
                    embed = await success_view.get_embed(f"Set the {self.channel_type} channel to https://discord.com/channels/{interaction.guild.id}/{channel.id}"),
                    view=success_view
                )
            else:
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed(f"Channel ID `{channel.id}` doesn't exist."),
                    view=failure_view
                )

        self.channel_select.callback = select_callback
        self.create_channel_button.callback = button_callback
        self.add_item(self.channel_select)
        self.add_item(self.create_channel_button)
        self.add_item(self.go_back)

    async def on_timeout(self):
        self.result = None
        self.create_channel_button.disabled = True
        self.go_back.disabled = True
        self.stop()

    async def get_embed(self, description):
        embed = discord.Embed(
            title="RoInvites Setup",
            description=description,
            color=discord.Color.dark_gold()
        )
        return embed

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(
        placeholder="Choose an option...",
        options=[
            discord.SelectOption(label="Invite Channel", value="invite", emoji="👥", description="Control where invite/leave messages are sent"),
            discord.SelectOption(label="Announcement Channel", value="announcement", emoji="📢", description="Control where global announcements are sent")
        ]
    )
    async def callback(self, interaction: discord.Interaction, select):
        if select.values[0] in ["invite", "announcement"]:
            channel_view = ChannelView(select.values[0])
            await interaction.response.edit_message(
                embed=await channel_view.get_embed(f"Set the {select.values[0]} channel:"),
                view=channel_view
            )
            await channel_view.wait()

            result = channel_view.result
            if result is None:
                return
            channel = result.resolve()
            permissions = channel.permissions_for(interaction.guild.me)
            if not (
                permissions.view_channel and
                permissions.send_messages and
                permissions.embed_links
            ):
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed(f"I don't have the necessary permissions to operate in https://discord.com/channels/{interaction.guild.id}/{channel.id}.\nEnable the **View Channel**, **Send Messages**, and **Embed Links** permissions for me in that channel."),
                    view=failure_view
                )
                return

            success = await interaction.client.settings_manager.set_channel(interaction.guild, select.values[0], channel)
            if success:
                success_view = SuccessView()
                await interaction.edit_original_response(
                    embed=await success_view.get_embed(f"Set the {select.values[0]} channel to https://discord.com/channels/{interaction.guild.id}/{channel.id}"),
                    view=success_view
                )
            else:
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed(f"Channel ID `{channel.id}` doesn't exist."),
                    view=failure_view
                )

    async def on_timeout(self):
        self.stop()

    async def get_embed(self):
        embed = discord.Embed(
            title="RoInvites Setup",
            description="""
            Set an option to configure!
            You can configure the bot's channels, with much more being configurable soon.
            """,
            color=discord.Color.dark_gold()
        )
        return embed

class ServerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def user_autocomplete(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> list[app_commands.Choice[str]]:
        users = await interaction.client.user_manager.get_guild_users(interaction.guild)
        return [
            app_commands.Choice(name=user["username"], value=user["user_id"])
            for user in users
            if query.lower() in user["username"].lower()
        ]

    server = app_commands.Group(
        name="server",
        description="Server commands",
        allowed_installs=app_commands.AppInstallationType(
            guild=True,
            user=False
        ),
        allowed_contexts=app_commands.AppCommandContext(
            guild=True,
            dm_channel=False,
            private_channel=False
        )
    )

    @server.command(name="config", description="Configure RoInvites in this server")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config(
        self, 
        interaction: discord.Interaction
    ):
        view = SetupView()
        await interaction.response.send_message(embed=await view.get_embed(), view=view, ephemeral=True)
        await view.wait()

    @server.command(name="link", description="Links your account with the current server")
    async def link(
        self, 
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.user_manager.link_user(interaction.user, interaction.guild)
        if success == True:
            await interaction.followup.send(f"Successfully added you to this server!")
        else:
            await interaction.followup.send(success)

    @server.command(name="unlink", description="Unlinks you from the current server")
    async def unlink(
        self, 
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.user_manager.unlink_user(interaction.user, interaction.guild)
        if success == True:
            await interaction.followup.send(f"Removed you from this server. Hope you had a great time!")
        else:
            await interaction.followup.send(f"You don't have a Roblox account associated with RoInvites.\nAdd one with `/user config` > Add Account!")

    @server.command(name="pause_invites", description="Pauses sending invites pertaining to your account in the current server")
    async def pause_invites(
        self, 
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.user_manager.modify_server_invites(interaction.user, interaction.guild, 1)
        if success == True:
            await interaction.followup.send(f"Successfully paused messages related to your account in this server!")
        else:
            await interaction.followup.send(success)

    @server.command(name="resume_invites", description="Resumes sending invites pertaining to your account in the current server")
    async def resume_invites(
        self, 
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.user_manager.modify_server_invites(interaction.user, interaction.guild, 0)
        if success == True:
            await interaction.followup.send(f"Successfully resumed messages related to your account in this server!")
        else:
            await interaction.followup.send(success)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerCog(bot))
