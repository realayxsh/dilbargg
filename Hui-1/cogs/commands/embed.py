import discord
from discord.ext import commands
from discord import app_commands

OWNER_ROLE_ID = 1502876234705535088


def owner_role_check():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        role = ctx.guild.get_role(OWNER_ROLE_ID)
        if role and role in ctx.author.roles:
            return True
        container = discord.ui.Container(
            discord.ui.TextDisplay("<:cross:1077478135794245743> You do not have permission to use this command.")
        )
        await ctx.reply(components=[container], mention_author=False, delete_after=5)
        return False
    return commands.check(predicate)


class EmbedModal(discord.ui.Modal, title='Send Embed - Dilbar Support'):
    embed_title = discord.ui.TextInput(
        label='Title (optional)',
        placeholder='Embed title here',
        required=False,
        max_length=256,
    )
    description = discord.ui.TextInput(
        label='Description',
        style=discord.TextStyle.long,
        placeholder='Your embed message content here',
        required=True,
        max_length=2000,
    )
    color_hex = discord.ui.TextInput(
        label='Accent Color (optional hex, e.g. ff0000)',
        placeholder='Leave blank for transparent (no color)',
        required=False,
        max_length=7,
    )
    image_url = discord.ui.TextInput(
        label='Image URL (optional)',
        placeholder='https://...',
        required=False,
    )
    footer_text = discord.ui.TextInput(
        label='Footer text (optional)',
        placeholder='Footer here',
        required=False,
        max_length=128,
    )

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        title = self.embed_title.value or None
        desc = self.description.value
        image = self.image_url.value or None
        footer = self.footer_text.value or None

        parts = []
        if title:
            parts.append(f"## {title}")
        parts.append(desc)
        if footer:
            parts.append(f"-# {footer}")

        text = "\n\n".join(parts)
        children = [discord.ui.TextDisplay(text)]
        if image:
            children.append(discord.ui.MediaGallery(
                discord.ui.MediaGalleryItem(media=image)
            ))

        container = discord.ui.Container(*children)
        await self.channel.send(components=[container])
        await interaction.response.send_message(
            f"<a:green_tick:1103363669263405157> Embed sent to {self.channel.mention}",
            ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Something went wrong.', ephemeral=True)


class EmbedSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sendembed", aliases=["se", "embed"])
    @owner_role_check()
    @commands.guild_only()
    async def send_embed(self, ctx, channel: discord.TextChannel, *, content: str = None):
        """Send a transparent V2 embed to any channel.
        Usage: -sendembed #channel message
        Use | to separate parts: title | description | hexcolor
        """
        await ctx.message.delete()

        title = None
        description = None
        color = None
        image = None

        if content:
            parts = [p.strip() for p in content.split("|")]
            if len(parts) == 1:
                description = parts[0]
            elif len(parts) == 2:
                title = parts[0] or None
                description = parts[1] or None
            elif len(parts) >= 3:
                title = parts[0] or None
                description = parts[1] or None
                image = parts[2] if parts[2].startswith('http') else None

        text_parts = []
        if title:
            text_parts.append(f"## {title}")
        if description:
            text_parts.append(description)
        if not text_parts:
            text_parts.append("\u200b")

        text = "\n\n".join(text_parts)
        children = [discord.ui.TextDisplay(text)]
        if image:
            children.append(discord.ui.MediaGallery(discord.ui.MediaGalleryItem(media=image)))

        container = discord.ui.Container(*children)
        await channel.send(components=[container])

        confirm = discord.ui.Container(
            discord.ui.TextDisplay(f"<a:green_tick:1103363669263405157> Embed sent to {channel.mention}")
        )
        msg = await ctx.send(components=[confirm])
        await msg.delete(delay=5)

    @app_commands.command(name="sendembed", description="Send a custom transparent embed to a channel")
    @app_commands.describe(channel="The channel to send the embed to")
    async def slash_send_embed(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        role = interaction.guild.get_role(OWNER_ROLE_ID)
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this.", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedModal(channel))


async def setup(client):
    await client.add_cog(EmbedSender(client))
