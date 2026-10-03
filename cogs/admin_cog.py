import discord
import logging
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

class AnnouncementModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Create Announcement")
        self.value = None
        
        self.announcement_input = discord.ui.TextInput(
            label="Announcement",
            placeholder="Enter announcement message...",
            style=discord.TextStyle.long
        )
        self.add_item(self.announcement_input)

        self.hex_input = discord.ui.TextInput(
            label="Hex Color",
            placeholder="Enter hex color... (optional)",
            required=False,
            min_length=6,
            max_length=7
        )
        self.add_item(self.hex_input)

        self.announcement_image_input = discord.ui.FileUpload(
            custom_id="announcement_image",
            required=False,
            min_values=1,
            max_values=1
        )

        self.label_container = discord.ui.Label(
            text="Upload Image",
            description="Upload an image with your announcement. (optional)",
            component=self.announcement_image_input
        )
        self.add_item(self.label_container)

    async def on_submit(self, interaction: discord.Interaction):
        self.value = self.announcement_input.value
        await interaction.response.defer()

        embed = discord.Embed(
            title="Global Announcement",
            description=self.value,
            color=discord.Color.dark_purple() if self.hex_input.value.strip() == "" else int(self.hex_input.value, 16),
        )

        user_id = await interaction.client.user_manager.get_user_from_discord_id(interaction.user)
        if user_id is not None:
            username = await interaction.client.user_manager.get_username(user_id)
            display_name = await interaction.client.user_manager.get_display_name(user_id)
            if not None in (username, display_name):
                embed.title = f"Announcement from {display_name}"
            thumbnail_url = await interaction.client.api.get_avatar_headshot(user_id)
            if thumbnail_url is not None:
                embed.set_thumbnail(url=thumbnail_url)

        allowed_extensions = (".png", ".jpg", ".jpeg")
        attachments = self.announcement_image_input.values
        if attachments:
            target_file = attachments[0] if isinstance(attachments, list) else attachments
            if target_file.filename.lower().endswith(allowed_extensions):
                embed.set_image(url=target_file.url)
            else:
                await interaction.followup.send("The uploaded image must be a .png, .jpg, or .jpeg file.", ephemeral=True)
                return

        for guild in interaction.client.guilds:
            announcement_channel = await interaction.client.settings_manager.get_channel(guild, "announcement")
            try:
                channel = interaction.client.get_channel(announcement_channel)
                await channel.send(embed=embed)
            except:
                pass

        logger.info(f"Sent global announcement: {self.value[:20].replace("\n", " ")}...")
        await interaction.followup.send("Successfully sent announcement!", ephemeral=True)

    async def on_timeout(self):
        self.stop()

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def user_autocomplete(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> list[app_commands.Choice[str]]:
        users = await interaction.client.user_manager.get_all_users()
        return [
            app_commands.Choice(name=data["username"], value=user_id)
            for user_id, data in users.items()
            if query.lower() in data["username"].lower()
        ]

    admin = app_commands.Group(
        name="admin",
        description="Admin commands",
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

    @admin.command(name="remove", description="Removes a user from RoInvites")
    @app_commands.autocomplete(user_id=user_autocomplete)
    async def admin_remove_user(
        self, 
        interaction: discord.Interaction,
        user_id: int
    ):
        if not (
            await self.bot.user_manager.is_admin(interaction.user) or
            await self.bot.is_owner(interaction.user)
        ):
            await interaction.response.send_message(f"You are not an admin.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        success = await interaction.client.user_manager.remove_user_id(user_id)
        if success == True:
            logger.info(f"Removed user with ID {user_id} from RoInvites")
            await interaction.followup.send(f"Removed this user from RoInvites.")
        else:
            await interaction.followup.send(f"This user isn't associated with RoInvites.")

    @admin.command(name="announce", description="Sends a global announcement")
    async def send_announcement(
        self, 
        interaction: discord.Interaction,
    ):
        if not (
            await self.bot.user_manager.is_admin(interaction.user) or
            await self.bot.is_owner(interaction.user)
        ):
            await interaction.response.send_message(f"You are not an admin.", ephemeral=True)
            return

        await interaction.response.send_modal(AnnouncementModal())

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
