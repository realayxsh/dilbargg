from discord.ext import commands
from core import Ventura, Cog
import discord, requests
import json
from utils.Tools import *
from discord.ui import View, Button
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
    datefmt="%H:%M:%S",
)


def _make_v2_guild_info(guild, client, event_name="Guild Joined"):
    channels = len(set(client.get_all_channels()))
    lines = [
        f"## {event_name}: {guild.name}",
        f"**Name:** {guild.name}\n**ID:** {guild.id}\n**Owner:** {guild.owner} (<@{guild.owner_id}>)\n"
        f"**Created:** {guild.created_at.month}/{guild.created_at.day}/{guild.created_at.year}\n"
        f"**Members:** {len(guild.members)}",
    ]
    if guild.description:
        lines.append(f"**Description**\n{guild.description}")
    if guild.features:
        lines.append("**Features**\n" + "\n".join(f.replace("_", " ").title() for f in guild.features))
    lines.append(
        f"**Members:** {len(guild.members)} | Humans: {len([m for m in guild.members if not m.bot])} | Bots: {len([m for m in guild.members if m.bot])}"
    )
    lines.append(
        f"**Channels:** {len(guild.text_channels)} text / {len(guild.voice_channels)} voice / {len(guild.categories)} categories"
    )
    lines.append(f"**Bot Info:** Servers: `{len(client.guilds)}` | Users: `{len(client.users)}` | Channels: `{channels}`")
    return discord.ui.Container(discord.ui.TextDisplay("\n\n".join(lines)))


class Guild(Cog):
    def __init__(self, client: Ventura):
        self.client = client

    @commands.Cog.listener(name="on_guild_join")
    async def hacker(self, guild):
        rope = [inv for inv in await guild.invites() if inv.max_age == 0 and inv.max_uses == 0]
        me = self.client.get_channel(1093258327116480522)
        if me:
            container = _make_v2_guild_info(guild, self.client, "Guild Joined")
            await me.send(
                f"{rope[0]}" if rope else "No Pre-Made Invite Found",
                components=[container]
            )

        if not guild.chunked:
            await guild.chunk()

        welcome_container = discord.ui.Container(
            discord.ui.TextDisplay(
                f"## 👋 Hey, I am Dilbar Support!\n"
                "Thank you for adding me to your server.\n\n"
                "**Help** — Sends the help page.\n"
                "**Botinfo** — Shows info about the bot."
            )
        )
        channel = discord.utils.get(guild.text_channels, name="general")
        if not channel:
            channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
            if channels:
                channel = channels[0]
        if channel:
            await channel.send(components=[welcome_container])

    @commands.Cog.listener(name="on_guild_remove")
    async def on_g_remove(self, guild):
        idk = self.client.get_channel(1074237489151221811)
        if idk:
            container = _make_v2_guild_info(guild, self.client, "Guild Removed")
            await idk.send(components=[container])

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("config.json", "r") as f:
            data = json.load(f)
        if str(guild.id) in data["guilds"]:
            del data["guilds"][str(guild.id)]
            with open("config.json", "w") as f:
                json.dump(data, f)

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        logging.info("Shard #%s is ready" % shard_id)

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        logging.info("Shard #%s has connected" % shard_id)

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        logging.info("Shard #%s has disconnected" % shard_id)

    @commands.Cog.listener()
    async def on_shard_resume(self, shard_id):
        logging.info("Shard #%s has resumed" % shard_id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        log = self.client.get_channel(1073111868496957530)
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            if log:
                container = discord.ui.Container(
                    discord.ui.TextDisplay(f"**Error from:** {ctx.author}\n{error}")
                )
                await log.send(components=[container])
