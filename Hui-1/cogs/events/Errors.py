import discord, json
from discord.ext import commands
from core import Ventura, Cog, Context
from utils.v2embed import reply_v2, send_v2

class Errors(Cog):
  def __init__(self, client: Ventura):
    self.client = client

  @commands.Cog.listener()
  async def on_command_error(self, ctx: Context, error):
    with open('ignore.json', 'r') as heck:
      randi = json.load(heck)
    with open('blacklist.json', 'r') as f:
      data = json.load(f)
    if isinstance(error, commands.CommandNotFound):
      return
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CheckFailure):
      if str(ctx.author.id) in data["ids"]:
        await reply_v2(ctx,
          "<a:red_cross:1103371611983327322> **Blacklisted**\nYou Are Blacklisted From Using My Commands.\nIf You Think That It Is A Mistake, Contact The Server Owner.",
          mention_author=False)
      if str(ctx.channel.id) in randi["ids"]:
        await ctx.reply(f"My all commands are disabled for {ctx.channel.mention}", mention_author=True, delete_after=6)
    elif isinstance(error, commands.NoPrivateMessage):
      await reply_v2(ctx, "You Can't Use My Commands In DMs.", delete_after=20, mention_author=False)
    elif isinstance(error, commands.TooManyArguments):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CommandOnCooldown):
      await reply_v2(ctx,
        f"<a:war:1085999886459228292> | {ctx.author.name} is on cooldown, retry after **{error.retry_after:.2f}s**",
        delete_after=10, mention_author=False)
    elif isinstance(error, commands.MaxConcurrencyReached):
      await reply_v2(ctx,
        "<a:war:1085999886459228292> | This command is already running, let it finish and retry.",
        delete_after=10, mention_author=False)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MissingPermissions):
      missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_permissions]
      fmt = " and ".join(missing) if len(missing) <= 2 else "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
      await reply_v2(ctx,
        f"<a:war:1085999886459228292> | You lack `{fmt}` permission(s) to run `{ctx.command.name}`!",
        delete_after=6, mention_author=False)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.BadArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.BotMissingPermissions):
      missing = ", ".join(error.missing_perms)
      await send_v2(ctx, f"I need the **{missing}** permission(s) to run **{ctx.command.name}**!", delete_after=10)
    elif isinstance(error, discord.HTTPException):
      pass
    elif isinstance(error, commands.CommandInvokeError):
      pass
