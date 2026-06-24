import discord
from discord.ext import commands
import datetime
import re
import json
from core import Ventura, Cog
from utils.Tools import getConfig
from utils.v2embed import send_v2


class AntiSpam(Cog):
    def __init__(self, client: Ventura):
        self.client = client
        self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(4, 7, commands.BucketType.member)
        self.spam_punish_cooldown_cd_mapping = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.member)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        mem = message.author
        invite_regex = re.compile(r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?")
        link_regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        invite_matches = invite_regex.findall(message.content)
        link_matches = link_regex.findall(message.content)
        data = getConfig(message.guild.id)
        antiSpam = data["antiSpam"]
        antiLink = data["antiLink"]
        wled = data["whitelisted"]
        wlrole = data['wlrole']
        hacker = message.guild.get_member(message.author.id)
        wlroles = message.guild.get_role(wlrole)
        try:
            if antiSpam is True:
                if mem.guild_permissions.administrator or str(message.author.id) in wled or wlroles in hacker.roles:
                    return
                bucket = self.spam_cd_mapping.get_bucket(message)
                retry = bucket.update_rate_limit()
                if retry:
                    now = discord.utils.utcnow()
                    await message.author.timeout(now + datetime.timedelta(minutes=15), reason="Dilbar <3 | Anti Spam")
                    await send_v2(message.channel,
                        f"<a:green_tick:1103363669263405157> | Successfully muted {message.author.mention} for **spamming**.")

            if antiLink is True:
                if mem.guild_permissions.administrator or str(message.author.id) in wled or wlroles in hacker.roles:
                    return
                now = discord.utils.utcnow()
                if invite_matches:
                    await message.delete()
                    await message.author.timeout(now + datetime.timedelta(minutes=15), reason="Dilbar <3 | Anti Discord Invites")
                    await send_v2(message.channel,
                        f"<a:green_tick:1103363669263405157> | Muted {message.author.mention} for sending **Discord invites**.")
                elif link_matches:
                    await message.author.timeout(now + datetime.timedelta(minutes=15), reason="Dilbar <3 | Anti Link")
                    await send_v2(message.channel,
                        f"<a:green_tick:1103363669263405157> | Muted {message.author.mention} for sending **links**.")
        except Exception as error:
            print(error)
