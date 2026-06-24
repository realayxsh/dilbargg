import os
import discord
from discord.ext import commands
from utils.Tools import getConfig, add_user_to_blacklist, getanti
from discord.ui import View, Button
import json
from core import Ventura, Cog
from utils.v2embed import send_v2


class antipinginv(Cog):
    def __init__(self, client: Ventura):
        self.client = client
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_message(self, message):
        button = Button(emoji="<:invite:1073159512049057832>", label="Invite",
                        url="https://discord.com/api/oauth2/authorize?client_id=1097475016880304180&permissions=8&scope=bot%20applications.commands")
        button1 = Button(emoji="<:SupportTeam:1073159959866511370>", label="Support",
                         url="https://discord.gg/HyWQdHjNPz")
        try:
            with open("blacklist.json", "r") as f:
                data2 = json.load(f)
            with open('ignore.json', 'r') as heck:
                randi = json.load(heck)
                ventura = '<@1097475016880304180>'
                try:
                    data = getConfig(message.guild.id)
                    anti = getanti(message.guild.id)
                    wled = data["whitelisted"]
                    punishment = data["punishment"]
                    wlrole = data['wlrole']
                    guild = message.guild
                    hacker = guild.get_member(message.author.id)
                    wlroles = guild.get_role(wlrole)
                except Exception:
                    pass
                guild = message.guild
                if message.mention_everyone:
                    if str(message.author.id) in wled or anti == "off" or wlroles in hacker.roles:
                        pass
                    else:
                        if punishment == "ban":
                            await message.guild.ban(message.author, reason="Mentioning Everyone | Not Whitelisted")
                        elif punishment == "kick":
                            await message.guild.kick(message.author, reason="Mentioning Everyone | Not Whitelisted")
                elif message.content == ventura or message.content == "<@!1097475016880304180>":
                    if str(message.author.id) in data2["ids"]:
                        await send_v2(message.channel,
                            "<a:red_cross:1103371611983327322> **Blacklisted**\nYou are blacklisted from using my commands.")
                        return
                    if str(message.channel.id) in randi["ids"]:
                        await message.reply(
                            f"My all commands are disabled for {message.channel.mention}",
                            mention_author=True, delete_after=10)
                        return
                    view = View()
                    view.add_item(button)
                    view.add_item(button1)
                    await send_v2(message.channel,
                        f"Hey! I'm **Dilbar Support**\n\nUse `-help` for a list of commands.",
                        view=view)
                else:
                    return
        except Exception as error:
            if isinstance(error, discord.Forbidden):
                return
