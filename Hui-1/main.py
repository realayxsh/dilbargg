import v2compat
v2compat.install()

import os
from core.Ventura import Ventura
import asyncio, json
import jishaku, cogs
from discord.ext import commands, tasks
import discord
from discord import app_commands
import traceback
from discord.ext.commands import Context
from discord import Spotify
from utils.components import patch_discord

patch_discord()

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

client = Ventura()
tree = client.tree


async def dilbar_stats():
    while True:
        servers = len(client.guilds)
        users = sum(g.member_count for g in client.guilds if g.member_count is not None)
        sv_ch = client.get_channel(1088668421740318790)
        users_ch = client.get_channel(1088668421740318790)
        await asyncio.sleep(3000)
        if sv_ch:
            await sv_ch.edit(name="Servers ; {}".format(servers))
        if users_ch:
            await users_ch.edit(name="Users ; {}".format(users))


@client.event
async def on_ready():
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")
    await client.loop.create_task(dilbar_stats())
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)


from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def home():
    return "PERFECTLY FINE"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


keep_alive()


@client.event
async def on_command_completion(context: Context) -> None:
    full_command_name = context.command.qualified_name
    split = full_command_name.split("\n")
    executed_command = str(split[0])
    devansh = client.get_channel(1088668421740318790)
    if context.guild is not None:
        try:
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    f"**Command:** {executed_command}\n"
                    f"**By:** {context.author} (ID: {context.author.id})\n"
                    f"**Guild:** {context.guild.name} (ID: {context.guild.id})\n"
                    f"**Channel:** #{context.channel.name}"
                )
            )
            if devansh:
                await devansh.send(components=[container])
        except Exception:
            print('PERFECTLY FINE')


@client.command()
async def spotify(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    if user.activities:
        for activity in user.activities:
            if isinstance(activity, Spotify):
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        f"## {user.name}'s Spotify\nListening to **{activity.title}**\n\n"
                        f"**Artist:** {activity.artist}\n**Album:** {activity.album}\n"
                        f"-# Song started at {activity.created_at.strftime('%H:%M')}"
                    ),
                    discord.ui.MediaGallery(
                        discord.ui.MediaGalleryItem(media=activity.album_cover_url)
                    )
                )
                await ctx.send(components=[container])


async def main():
    async with client:
        os.system("clear")
        await client.load_extension("cogs")
        await client.load_extension("jishaku")
        await client.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
