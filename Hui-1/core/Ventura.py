from __future__ import annotations
from discord.ext import commands
import discord
import aiohttp
import json
import jishaku, time
import asyncio
import typing
from utils.config import OWNER_IDS, EXTENSIONS, No_Prefix
from utils import getConfig, updateConfig, DotEnv
from .Context import Context
from discord.ext import commands, tasks

# The bot is restricted to this server only
ALLOWED_GUILD_ID = 1359524927019028670
# Only members with this role can use commands (except -afk which is open to everyone)
OWNER_ROLE_ID = 1502876234705535088
VC_CHANNEL_ID = 1502876369468657674


class Ventura(commands.AutoShardedBot):

    def __init__(self, *arg, **kwargs):
        intents = discord.Intents.all()
        intents.presences = False
        intents.members = False
        super().__init__(command_prefix=self.get_prefix,
                         case_insensitive=True,
                         intents=intents,
                         status=discord.Status.dnd,
                         strip_after_prefix=True,
                         owner_ids=OWNER_IDS,
                         allowed_mentions=discord.AllowedMentions(
                             everyone=False, replied_user=False, roles=False),
                         sync_commands_debug=True,
                         sync_commands=True,
                         shard_count=1)

    async def on_ready(self):
        print("Connected as {}".format(self.user))

    async def on_connect(self):
        await self.change_presence(status=discord.Status.idle,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.listening,
                                       name='-help'))

    @tasks.loop(seconds=30)
    async def vc_keep_alive(self):
        """Ensure the bot stays connected to the designated VC channel."""
        channel = self.get_channel(VC_CHANNEL_ID)
        if channel is None or not isinstance(channel, discord.VoiceChannel):
            return
        guild = channel.guild
        vc = guild.voice_client
        if vc is None:
            try:
                await channel.connect(self_deaf=True)
                print(f"Joined VC: {channel.name}")
            except Exception as e:
                print(f"Failed to join VC: {e}")
        elif vc.channel.id != VC_CHANNEL_ID:
            try:
                await vc.move_to(channel)
            except Exception as e:
                print(f"Failed to move to VC: {e}")

    @vc_keep_alive.before_loop
    async def before_vc_keep_alive(self):
        await self.wait_until_ready()

    async def send_raw(self, channel_id: int, content: str,
                       **kwargs) -> typing.Optional[discord.Message]:
        await self.http.send_message(channel_id, content, **kwargs)

    async def invoke_help_command(self, ctx: Context) -> None:
        """Invoke the help command or default help command if help extensions is not loaded."""
        return await ctx.send_help(ctx.command)

    async def fetch_message_by_channel(
            self, channel: discord.TextChannel,
            messageID: int) -> typing.Optional[discord.Message]:
        async for msg in channel.history(
                limit=1,
                before=discord.Object(messageID + 1),
                after=discord.Object(messageID - 1),
        ):
            return msg

    async def get_prefix(self, message: discord.Message):
        with open('info.json', 'r') as f:
            p = json.load(f)
        if message.author.id in p["np"]:
            return commands.when_mentioned_or('-', '')(self, message)
        else:
            if message.guild:
                data = getConfig(message.guild.id)
                prefix = data["prefix"]
                return commands.when_mentioned_or('-')(self, message)
            else:
                return commands.when_mentioned_or('-')(self, message)

    async def on_message_edit(self, before, after):
        ctx: Context = await self.get_context(after, cls=Context)
        if before.content != after.content:
            if after.guild is None or after.author.bot:
                return
            if ctx.command is None:
                return
            if type(ctx.channel) == "public_thread":
                return
            await self.invoke(ctx)
        else:
            return

    async def process_commands(self, message: discord.Message):
        # Ignore messages from bots
        if message.author.bot:
            return

        ctx: Context = await self.get_context(message, cls=Context)

        if ctx.command is None:
            return

        # Only allow commands in the designated server
        if message.guild is None or message.guild.id != ALLOWED_GUILD_ID:
            return

        # AFK command is open to everyone on the server — skip the role check
        if ctx.command.qualified_name == "afk":
            await self.invoke(ctx)
            return

        # All other commands require the owner role
        role = message.guild.get_role(OWNER_ROLE_ID)
        if role is None or role not in message.author.roles:
            return  # Silently ignore — no error message for unauthorized users

        await self.invoke(ctx)
