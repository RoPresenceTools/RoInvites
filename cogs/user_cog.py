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
        main_menu_view = MainMenuView()
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

class UsernameModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Enter Roblox Username")
        self.value = None
        self.username_input = discord.ui.TextInput(
            label="Username",
            placeholder="Enter your Roblox username..."
        )
        self.add_item(self.username_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.value = self.username_input.value
        await interaction.response.defer()

    async def on_timeout(self):
        self.stop()

class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(
        placeholder="Choose an option...",
        options=[
            discord.SelectOption(label="Add Account", value="add", emoji="➕", description="Add your Roblox account to RoInvites"),
            discord.SelectOption(label="Remove Account", value="remove", emoji="❌", description="Remove your Roblox account from RoInvites"),
            discord.SelectOption(label="Freeze Account", value="freeze", emoji="❄️", description="Freeze your RoInvites account"),
            discord.SelectOption(label="Unfreeze Account", value="unfreeze", emoji="🔥", description="Unfreeze your RoInvites account"),
            discord.SelectOption(label="Refresh User Info", value="refresh", emoji="🔄", description="Refresh your username and display name")
        ]
    )
    async def callback(self, interaction: discord.Interaction, select):
        if select.values[0] == "add":
            username_modal = UsernameModal()
            await interaction.response.send_modal(username_modal)
            await username_modal.wait()

            username = username_modal.value
            if username.strip() == "":
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed("No username was given."),
                    view=failure_view
                )
                return

            success = await interaction.client.user_manager.add_user(username, interaction.user)
            if success == True:
                success_view = SuccessView()
                await interaction.edit_original_response(
                    embed=await success_view.get_embed(f"Successfully added you (@{username}) to RoInvites!\nRun `/server link` in any server with me in it to participate in leaderboards and events!"),
                    view=success_view
                )
            else:
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed(success),
                    view=failure_view
                )
        elif select.values[0] == "remove":
            username_modal = UsernameModal()
            await interaction.response.send_modal(username_modal)
            await username_modal.wait()

            username = username_modal.value
            if username.strip() == "":
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed("No username was given."),
                    view=failure_view
                )
                return

            stored_user_id = await interaction.client.user_manager.get_user_from_discord_id(interaction.user)
            stored_username = await interaction.client.user_manager.get_username(stored_user_id)

            if stored_username is None:
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed = await failure_view.get_embed(f"You don't have a Roblox account associated with RoInvites.\nAdd one with `/user config` > Add Account!"),
                    view=failure_view
                )
                return

            if username.lower() != stored_username.lower():
                failure_view = FailureView()
                await interaction.edit_original_response(
                    embed=await failure_view.get_embed("This username does not match the Roblox username we have on file.\nAborted account deletion."),
                    view=failure_view
                )
                return
            
            success = await interaction.client.user_manager.remove_user(interaction.user)
            if success == True:
                success_view = SuccessView()
                await interaction.edit_original_response(
                    embed=await success_view.get_embed(f"Successfully removed you from RoInvites.\nHope you had a great time!"),
                    view=success_view
                )
        elif select.values[0] == "freeze":
            success = await interaction.client.user_manager.modify_freeze_user(interaction.user, 1)
            if success == True:
                success_view = SuccessView()
                await interaction.response.edit_message(
                    embed=await success_view.get_embed(f"Successfully froze your account!"),
                    view=success_view
                )
            else:
                failure_view = FailureView()
                await interaction.response.edit_message(
                    embed=await failure_view.get_embed(f"You don't have a Roblox account associated with RoInvites.\nAdd one with `/user config` > Add Account!"),
                    view=failure_view
                )
        elif select.values[0] == "unfreeze":
            success = await interaction.client.user_manager.modify_freeze_user(interaction.user, 0)
            if success == True:
                success_view = SuccessView()
                await interaction.response.edit_message(
                    embed=await success_view.get_embed(f"Successfully unfroze your account!"),
                    view=success_view
                )
            else:
                failure_view = FailureView()
                await interaction.response.edit_message(
                    embed=await failure_view.get_embed(f"You don't have a Roblox account associated with RoInvites.\nAdd one with `/user config` > Add Account!"),
                    view=failure_view
                )
        elif select.values[0] == "refresh":
            success = await interaction.client.user_manager.update_user_info(interaction.user)
            if success == True:
                success_view = SuccessView()
                await interaction.response.edit_message(
                    embed=await success_view.get_embed("Successfully updated your user info!"),
                    view=success_view
                )
            else:
                failure_view = FailureView()
                await interaction.response.edit_message(
                    embed=await failure_view.get_embed(success),
                    view=failure_view
                )

    async def on_timeout(self):
        self.stop()

    async def get_embed(self):
        embed = discord.Embed(
            title="RoInvites Account Menu",
            description="""            
            **Select an option below:**
            1. Add your Roblox account
            2. Remove your account
            3. Freeze your account
            4. Unfreeze your account
            5. Refresh your username and display name
            """,
            color=discord.Color.dark_gold()
        )
        return embed

class UserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    user = app_commands.Group(
        name="user",
        description="User commands",
        allowed_installs=app_commands.AppInstallationType(
            guild=True,
            user=True
        ),
        allowed_contexts=app_commands.AppCommandContext(
            guild=True,
            dm_channel=True,
            private_channel=True
        )
    )

    @user.command(name="config", description="Configure your RoInvites account")
    async def add_user(
        self, 
        interaction: discord.Interaction
    ):
        view = MainMenuView()
        await interaction.response.send_message(embed=await view.get_embed(), view=view, ephemeral=True)
        await view.wait()

    @user.command(name="my_stats", description="Shows your statistics")
    async def get_user_card_dms(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()
        message_title, message_content = await interaction.client.leaderboard_manager.get_user_stats(discord_user=interaction.user, mode="user")
        embed = discord.Embed(
            title=message_title,
            description=message_content,
            color=discord.Color.dark_gold() if message_title != "Error" else red
        )

        user_id = await self.bot.user_manager.get_user_from_discord_id(interaction.user)
        thumbnail_url = await self.bot.api.get_avatar_headshot(user_id)
        if thumbnail_url is not None:
            embed.set_thumbnail(url=thumbnail_url)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="send_invite", description="Sends out your own personal invite card!")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(
        guilds=True,
        dms=True,
        private_channels=True
    )
    async def send_invite(
        self, 
        interaction: discord.Interaction
    ):
        await interaction.response.defer()
        (message_title, message_content, join_url) = await interaction.client.notifier.create_invite_card(interaction.user)
        embed = discord.Embed(
            title=message_title,
            description=message_content,
            color=discord.Color.dark_purple() if message_title != "Error" else red
        )

        user_id = await self.bot.user_manager.get_user_from_discord_id(interaction.user)
        thumbnail_url = await self.bot.api.get_avatar_headshot(user_id)
        if thumbnail_url is not None:
            embed.set_thumbnail(url=thumbnail_url)

        view = discord.ui.View()
        if join_url is not None:
            join_btn = discord.ui.Button(label="Join in Roblox", url=join_url)
            view.add_item(join_btn)

        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(UserCog(bot))
