import discord
from discord.ext import commands
import json
from typing import Optional
import time
from utils.Tools import *
from utils.v2embed import send_v2, reply_v2


afk_path = "database/afk.json"

black1 = 0
black2 = 0
black3 = 0


class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout: Optional[int] = None):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                content=f"Only **{self.ctx.author}** can use this. Run `{self.ctx.prefix}{self.ctx.command}` yourself.",
                ephemeral=True)
            return False
        return True


class OnOrOff(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=None)
        self.value = None

    @discord.ui.button(label="Yes", emoji="<:tick:1076042204310679562>", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(label="No", emoji="<:cross:1077478135794245743>", custom_id='No', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        self.value = 'No'
        self.stop()


class afk(commands.Cog):

    def __init__(self, client, *args, **kwargs):
        self.client = client

    async def time_formatter(self, seconds: float):
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = ((str(days) + " days, ") if days else "") + \
              ((str(hours) + " hours, ") if hours else "") + \
              ((str(minutes) + " minutes, ") if minutes else "") + \
              ((str(seconds) + " seconds, ") if seconds else "")
        return tmp[:-2]

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            with open(afk_path, 'r') as f:
                afk = json.load(f)
            if message.mentions:
                for user_mention in message.mentions:
                    if afk.get(f'{user_mention.id}', {}).get('AFK') == 'True':
                        if message.guild.id not in afk[f'{user_mention.id}']['guild']:
                            return
                        if message.author.bot:
                            return
                        reason = afk[f'{user_mention.id}']['reason']
                        ok = afk[f'{user_mention.id}']['time']
                        await send_v2(message.channel,
                            f'**{str(user_mention)}** went AFK <t:{ok}:R> : {reason}')

                        meeeth = int(afk[f'{user_mention.id}']['mentions']) + 1
                        afk[f'{user_mention.id}']['mentions'] = meeeth
                        with open(afk_path, 'w') as f:
                            json.dump(afk, f)

                        if afk[f'{user_mention.id}']['dm'] == 'True':
                            try:
                                await send_v2(user_mention,
                                    f'You were Mentioned in **{message.guild.name}** by **{message.author.name}**!',
                                    fields=[
                                        ("Total mentions", str(meeeth)),
                                        ("Contents", message.content),
                                        ("Jump URL", f"[Jump To Message]({message.jump_url})")
                                    ])
                            except Exception:
                                pass

                if afk.get(f'{message.author.id}', {}).get('AFK') == 'True':
                    hhh = afk[f'{message.author.id}']['guild']
                    if message.guild.id not in hhh:
                        return
                    meth = int(time.time()) - int(afk[f'{message.author.id}']['time'])
                    been_afk_for = await self.time_formatter(meth)
                    mentionz = afk[f'{message.author.id}']['mentions']
                    afk[f'{message.author.id}']['AFK'] = 'False'
                    afk[f'{message.author.id}']['guild'].remove(message.guild.id)
                    afk[f'{message.author.id}']['reason'] = None
                    await send_v2(message.channel,
                        f'Welcome back {message.author.mention}! You got **{mentionz}** mentions while AFK. AFK removed. You were away for **{been_afk_for}**.')
                    with open(afk_path, 'w') as f:
                        json.dump(afk, f)
                    try:
                        await message.author.edit(nick=message.author.display_name[5:])
                    except Exception:
                        pass
                    return

            if afk.get(f'{message.author.id}', {}).get('AFK') == 'True':
                hhh = afk[f'{message.author.id}']['guild']
                if message.guild.id not in hhh:
                    return
                meth = int(time.time()) - int(afk[f'{message.author.id}']['time'])
                been_afk_for = await self.time_formatter(meth)
                mentionz = afk[f'{message.author.id}']['mentions']
                afk[f'{message.author.id}']['AFK'] = 'False'
                if message.guild.id in afk[f'{message.author.id}']['guild']:
                    afk[f'{message.author.id}']['guild'].remove(message.guild.id)
                afk[f'{message.author.id}']['reason'] = None
                await send_v2(message.channel,
                    f'Welcome back {message.author.mention}! You got **{mentionz}** mentions while AFK. AFK removed. You were away for **{been_afk_for}**.')
            with open(afk_path, 'w') as f:
                json.dump(afk, f)
        except KeyError:
            pass

    @commands.hybrid_command(description="Set your AFK status in the server")
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    async def afk(self, ctx, *, reason=None):
        with open(afk_path, 'r') as f:
            afk = json.load(f)

        if not reason:
            reason = "I am afk"

        invite_patterns = ['discord.gg', 'DISCORD.GG', '.GG/', 'GG/', 'gg/', '.gg/']
        if any(p in reason for p in invite_patterns):
            return await send_v2(ctx, "You can't advertise in your AFK reason.")

        view = OnOrOff(ctx)
        test = await reply_v2(ctx,
            "**Shall the bot DM you on every mention while you're AFK?**",
            view=view, mention_author=False)
        await view.wait()

        if not f'{ctx.author.id}' in afk:
            afk[f'{ctx.author.id}'] = {}

        if not view.value:
            if test:
                await test.edit(content="Timed out.", components=[])
            return

        afk[f'{ctx.author.id}']['dm'] = 'True' if view.value == 'Yes' else 'False'
        afk[f'{ctx.author.id}']['AFK'] = 'True'
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        afk[f'{ctx.author.id}']['time'] = int(time.time())
        afk[f'{ctx.author.id}']['mentions'] = 0
        try:
            ok = afk[f'{ctx.author.id}']['guild']
            ok.append(ctx.guild.id)
            afk[f'{ctx.author.id}']['guild'] = ok
        except Exception:
            afk[f'{ctx.author.id}']['guild'] = [ctx.guild.id]

        if test:
            await test.delete()

        await send_v2(ctx, f'{ctx.author.mention} Your AFK is set to: **{reason}**')

        with open(afk_path, 'w') as f:
            json.dump(afk, f)


async def setup(client):
    await client.add_cog(afk(client))
