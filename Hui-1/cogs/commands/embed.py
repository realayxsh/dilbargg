import discord
from discord.ext import commands

# Only this role ID can use bot commands (besides afk which is open to all)
OWNER_ROLE_ID = 1502876234705535088

def owner_role_check():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        role = ctx.guild.get_role(OWNER_ROLE_ID)
        if role and role in ctx.author.roles:
            return True
        await ctx.reply(
            embed=discord.Embed(
                description="<:cross:1077478135794245743> You do not have permission to use this command.",
                color=0x2f3136
            ),
            mention_author=False,
            delete_after=5
        )
        return False
    return commands.check(predicate)


class EmbedSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sendembed", aliases=["se", "embed"])
    @owner_role_check()
    @commands.guild_only()
    async def send_embed(self, ctx, channel: discord.TextChannel, *, content: str = None):
        """Send a custom embed to any channel.
        Usage: -sendembed #channel [title | description | color]
        Separate parts with | :
          title | description
          title | description | #hexcolor
        If only one part is given it becomes the description.
        """
        await ctx.message.delete()

        title = None
        description = None
        color = 0x2f3136

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
                hex_str = parts[2].lstrip("#").strip()
                try:
                    color = int(hex_str, 16)
                except ValueError:
                    pass

        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=ctx.guild.name)

        await channel.send(embed=embed)
        confirm = await ctx.send(
            embed=discord.Embed(
                description=f"<a:green_tick:1103363669263405157> Embed sent to {channel.mention}",
                color=0x2f3136
            )
        )
        # Auto-delete the confirmation after 5 seconds
        await confirm.delete(delay=5)
