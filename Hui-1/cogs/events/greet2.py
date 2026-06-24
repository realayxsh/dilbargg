import discord
from discord.ext import commands
from core import Cog, Ventura, Context
from utils.Tools import *
from utils.v2embed import send_v2


class greet(Cog):
    def __init__(self, bot: Ventura):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member):
        data = getDB(member.guild.id)
        msg = data["welcome"]["message"]
        chan = list(data["welcome"]["channel"])
        emtog = data["welcome"]["embed"]
        emping = data["welcome"]["ping"]
        emimage = data["welcome"]["image"]
        emthumbnail = data["welcome"]["thumbnail"]
        emautodel = data["welcome"]["autodel"]
        user = member
        if chan == []:
            return

        replacements = {
            "<<server.name>>": user.guild.name,
            "<<server.member_count>>": str(user.guild.member_count),
            "<<user.name>>": str(user),
            "<<user.mention>>": user.mention,
            "<<user.created_at>>": f"<t:{int(user.created_at.timestamp())}:F>",
            "<<user.joined_at>>": f"<t:{int(user.joined_at.timestamp())}:F>",
        }
        for k, v in replacements.items():
            if k in msg:
                msg = msg.replace(k, v)

        ping_content = f"{user.mention}" if emping else ""
        autodel = emautodel if emautodel != 0 else None

        for chh in chan:
            ch = self.bot.get_channel(int(chh))
            if ch is None:
                continue
            if emtog:
                await send_v2(ch,
                    msg,
                    image=emimage if emimage else None,
                    thumbnail=emthumbnail if emthumbnail else None,
                    delete_after=autodel,
                    content=ping_content if ping_content else discord.utils.MISSING)
            else:
                await ch.send(msg, delete_after=autodel)
