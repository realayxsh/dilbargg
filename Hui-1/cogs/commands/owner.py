from __future__ import annotations
from discord.ext import commands
from utils.Tools import *
from discord import *
from utils.config import OWNER_IDS, No_Prefix
import json, discord
import typing
import aiohttp
import base64
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator

from typing import Optional


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client
      
    @commands.command(name="slist")
    @commands.is_owner()
    async def slist(self, ctx):
        devansh37 = ([devansh for devansh in self.client.guilds])
        devansh37 = sorted(devansh37,
                         key=lambda devansh: devansh.member_count,
                         reverse=True)
        entries = [
            f"`[{i}]` | [{g.name}](https://discord.com/channels/{g.id}) - {g.member_count}"
            for i, g in enumerate(devansh37, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Server List of Ventura - {len(self.client.guilds)}",
            color=0x2f3136,
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    



    @commands.command(name="restart", help="Restarts the client.")
    @commands.is_owner()
    async def _restart(self, ctx: Context):
        await ctx.reply("Restarting!")
        restart_program()
      
    @commands.command(name="sync", help="Syncs all database.")
    @commands.is_owner()
    async def _sync(self, ctx):
        await ctx.reply("Syncing...", mention_author=False)
        with open('anti.json', 'r') as f:
            data = json.load(f)
        for guild in self.client.guilds:
            if str(guild.id) not in data['guild']:
                data['guilds'][str(guild.id)] = 'on'
                with open('anti.json', 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                pass
        with open('config.json', 'r') as f:
            data = json.load(f)
        for op in data["guilds"]:
            g = self.client.get_guild(int(op))
            if not g:
                data["guilds"].pop(str(op))
                with open('config.json', 'w') as f:
                    json.dump(data, f, indent=4)

    @commands.group(name="blacklist",
                    help="let's you add someone in blacklist",
                    aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            with open("blacklist.json") as file:
                blacklist = json.load(file)
                entries = [
                    f"`[{no}]` | <@!{mem}> (ID: {mem})"
                    for no, mem in enumerate(blacklist['ids'], start=1)
                ]
                paginator = Paginator(source=DescriptionEmbedPaginator(
                    entries=entries,
                    title=
                    f"List of Blacklisted users of Ventura - {len(blacklist['ids'])}",
                    description="",
                    per_page=10,
                    color=0x2f3136),
                                      ctx=ctx)
                await paginator.paginate()

    @blacklist.command(name="add")
    @commands.is_owner()
    async def blacklist_add(self, ctx: Context, member: discord.Member):
        try:
            with open('blacklist.json', 'r') as bl:
                blacklist = json.load(bl)
                if str(member.id) in blacklist["ids"]:
                    embed = discord.Embed(
                        title="Error!",
                        description=f"{member.name} is already blacklisted",
                        color=discord.Colour(0x2f3136))
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    add_user_to_blacklist(member.id)
                    embed = discord.Embed(
                        title="Blacklisted",
                        description=f"Successfully Blacklisted {member.name}",
                        color=discord.Colour(0x2f3136))
                    with open("blacklist.json") as file:
                        blacklist = json.load(file)
                        embed.set_footer(
                            text=
                            f"There are now {len(blacklist['ids'])} users in the blacklist"
                        )
                        await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(title="Error!",
                                  description=f"An Error Occurred",
                                  color=discord.Colour(0x2f3136))
            await ctx.reply(embed=embed, mention_author=False)

    @blacklist.command(name="remove")
    @commands.is_owner()
    async def blacklist_remove(self, ctx, member: discord.Member = None):
        try:
            remove_user_from_blacklist(member.id)
            embed = discord.Embed(
                title="User removed from blacklist",
                description=
                f"<a:green_tick:1103363669263405157> | **{member.name}** has been successfully removed from the blacklist",
                color=0x2f3136)
            with open("blacklist.json") as file:
                blacklist = json.load(file)
                embed.set_footer(
                    text=
                    f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{member.name}** is not in the blacklist.",
                color=0x2f3136)
            embed.set_thumbnail(url=f"{self.client.user.display_avatar.url}")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.group(
        name="np",
        help="Allows you to add someone in no prefix list (owner only command)"
    )
    @commands.is_owner()
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list")
    @commands.is_owner()
    async def np_list(self, ctx):
        with open("info.json") as f:
            np = json.load(f)
            nplist = np["np"]
            npl = ([await self.client.fetch_user(nplu) for nplu in nplist])
            npl = sorted(npl, key=lambda nop: nop.created_at)
            entries = [
                f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
                for no, mem in enumerate(npl, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"No Prefix of Ventura - {len(nplist)}",
                description="",
                per_page=10,
                color=0x2f3136),
                                  ctx=ctx)
            await paginator.paginate()

    @_np.command(name="add", help="Add user to no prefix")
    @commands.is_owner()
    async def np_add(self, ctx, user: discord.User):
        with open('info.json', 'r') as idk:
            data = json.load(idk)
        np = data["np"]
        if user.id in np:
            embed = discord.Embed(
                description=
                f"**The User You Provided Already In My No Prefix**",
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            data["np"].append(user.id)
        with open('info.json', 'w') as idk:
            json.dump(data, idk, indent=4)
            embed1 = discord.Embed(
                description=
                f"<a:green_tick:1103363669263405157> | Added no prefix to {user} for all",
                color=0x2f3136)
          
            await ctx.reply(embed=embed1)

    @_np.command(name="remove", help="Remove user from no prefix")
    @commands.is_owner()
    async def np_remove(self, ctx, user: discord.User):
        with open('info.json', 'r') as idk:
            data = json.load(idk)
        np = data["np"]
        if user.id not in np:
            embed = discord.Embed(
                description="**{} is not in no prefix!**".format(user),
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            data["np"].remove(user.id)
        with open('info.json', 'w') as idk:
            json.dump(data, idk, indent=4)
            embed2 = discord.Embed(
                description=
                f"<a:green_tick:1103363669263405157> | Removed no prefix from {user} for all",
                color=0x2f3136)

            await ctx.reply(embed=embed2)

    @commands.group(name="bdg", help="Allows owner to add badges for a user")
    @commands.is_owner()
    async def _badge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_badge.command(name="add",
                    aliases=["give"],
                    help="Add some badges to a user.")
    @commands.is_owner()
    async def badge_add(self, ctx, member: discord.Member, *, badge: str):
        ok = getbadges(member.id)
        if badge.lower() in ["own", "owner", "king"]:
            idk = "**<:King:1103728930277556284> OWNER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed2 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `OWNER` Badge To {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embed2)
        elif badge.lower() in ["staff", "support staff"]:
            idk = "**<:StaffBadge:1103729149169905795> STAFF**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed3 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `STAFF` Badge To {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embed3)
        elif badge.lower() in ["partner"]:
            idk = "**<:partners:1103962673823088712> PARTNER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed4 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `PARTNER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed4)
        elif badge.lower() in ["sponsor"]:
            idk = "**<:Owners:1081818301413466183> SPONSER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed5 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `SPONSER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed5)
        elif badge.lower() in [
                "friend", "friends", "homies", "owner's friend"
        ]:
            idk = "**<:friends:1103962999267528714> FRIENDS**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed1 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `FRIENDS` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed1)
        elif badge.lower() in ["early", "supporter", "support"]:
            idk = "**<:EarlySupport:1103963190192259142> SUPPORTER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed6 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `SUPPORTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed6)

        elif badge.lower() in ["vip"]:
            idk = "**<:vippnehbb:1103963381783855135> VIP**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed7 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `VIP` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed7)

        elif badge.lower() in ["bug", "hunter"]:
            idk = "**<:Bug_hunter_2:1103963588902801428> BUG HUNTER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed8 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `BUG HUNTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed8)
        elif badge.lower() in ["all"]:
            idk = "**<:King:1103728930277556284> OWNER\n<:StaffBadge:1103729149169905795> STAFF\n<:partners:1103962673823088712> PARTNER\n<:Owners:1081818301413466183> SPONSER\n<:friends:1103962999267528714> FRIENDS\n<:EarlySupport:1103963190192259142> SUPPORTER\n<:vippnehbb:1103963381783855135> VIP\n<:Bug_hunter_2:1103963588902801428> BUG HUNTER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embedall = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Added `All` Badges To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embedall)
        else:
            hacker = discord.Embed(
                                   description="**Invalid Badge**",
                                   color=0x2f3136)
            
            await ctx.reply(embed=hacker)

    @_badge.command(name="remove",
                    help="Remove badges from a user.",
                    aliases=["re"])
    @commands.is_owner()
    async def badge_remove(self, ctx, member: discord.Member, *, badge: str):
        ok = getbadges(member.id)
        if badge.lower() in ["own", "owner", "king"]:
            idk = "**<:crown1:1072718187147300924> OWNER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed2 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `OWNER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed2)

        elif badge.lower() in ["staff", "support staff"]:
            idk = "**<a:ventura_staff:1072720458585223279> STAFF**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed3 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `STAFF` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed3)

        elif badge.lower() in ["partner"]:
            idk = "**<:PartneredServerOwner:1072720583973949511> PARTNER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed4 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `PARTNER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed4)

        elif badge.lower() in ["sponsor"]:
            idk = "**<a:diamond:1073099102193197086> SPONSER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed5 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `SPONSER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed5)

        elif badge.lower() in [
                "friend", "friends", "homies", "owner's friend"
        ]:
            idk = "**<:ventura_friends:1073099248410841150> FRIENDS**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed1 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `FRIENDS` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed1)

        elif badge.lower() in ["early", "supporter", "support"]:
            idk = "**<a:astroz_early:1073099540221141084> SUPPORTER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed6 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `SUPPORTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed6)

        elif badge.lower() in ["vip"]:
            idk = "**<:VIP:1073099724678242355> VIP**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed7 = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `VIP` Badge To {member}**",
                color=0x2f3136)
           
            await ctx.reply(embed=embed7)

        elif badge.lower() in ["bug", "hunter"]:
            idk = "**<a:astroz_bug:1073100013938409482> BUG HUNTER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed8 = discord.Embed(
                
                description=
                f"**Successfully Removed `BUG HUNTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed8)
        elif badge.lower() in ["all"]:
            idk = "**<a:CROWN:1096460289492393994> OWNER\n<a:staff:1096460645249064990> STAFF\n<a:partner:1096460876673990768> PARTNER\n<:Sponcer:1096461095637635134> SPONSER\n<:friends:1096461299770216531> FRIENDS\n<a:supporter_gif:1096461566670549085> SUPPORTER\n<:vip:1096461907935907870> VIP\n<a:bug_hunter:1096462124777218110> BUG HUNTER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embedall = discord.Embed(
                
                description=
                f"<a:green_tick:1103363669263405157> | **Successfully Removed `All` Badges From {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embedall)
        else:
            hacker = discord.Embed(
                                   description="**Invalid Badge**",
                                   color=0x2f3136)
            await ctx.reply(embed=hacker)




    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        """ DM the user of your choice """
        try:
            await user.send(message)
            await ctx.send(f"<a:green_tick:1103363669263405157> | Successfully Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")           



    @commands.group()
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))
            
            
    @change.command(name="nickname")
    @commands.is_owner()
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"<a:green_tick:1103363669263405157> | Successfully changed nickname to **{name}**")
            else:
                await ctx.send("<a:green_tick:1103363669263405157> | Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)



    @commands.group(name="adduser", invoke_without_command=True,
                    help="Grant a member permission to use the bot.")
    @commands.is_owner()
    async def adduser(self, ctx, member: discord.Member = None):
        if member is None:
            return await ctx.reply("Please mention a member. Usage: `adduser @member`", mention_author=False)
        from core.Ventura import OWNER_ROLE_ID
        role = ctx.guild.get_role(OWNER_ROLE_ID)
        if role is None:
            return await ctx.reply("Authorized role not found in this server.", mention_author=False)
        if role in member.roles:
            embed = discord.Embed(
                description=f"**{member}** already has bot access.",
                color=0x2f3136)
            return await ctx.reply(embed=embed, mention_author=False)
        await member.add_roles(role, reason=f"Bot access granted by {ctx.author}")
        embed = discord.Embed(
            description=f"<a:green_tick:1103363669263405157> | **{member}** has been granted access to use the bot.",
            color=0x2f3136)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.group(name="removeuser", invoke_without_command=True,
                    help="Revoke a member's permission to use the bot.")
    @commands.is_owner()
    async def removeuser(self, ctx, member: discord.Member = None):
        if member is None:
            return await ctx.reply("Please mention a member. Usage: `removeuser @member`", mention_author=False)
        from core.Ventura import OWNER_ROLE_ID
        role = ctx.guild.get_role(OWNER_ROLE_ID)
        if role is None:
            return await ctx.reply("Authorized role not found in this server.", mention_author=False)
        if role not in member.roles:
            embed = discord.Embed(
                description=f"**{member}** does not have bot access.",
                color=0x2f3136)
            return await ctx.reply(embed=embed, mention_author=False)
        await member.remove_roles(role, reason=f"Bot access revoked by {ctx.author}")
        embed = discord.Embed(
            description=f"<a:green_tick:1103363669263405157> | **{member}**'s bot access has been removed.",
            color=0x2f3136)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="setavatar", help="Change the bot's profile picture. Attach an image or provide a URL.")
    @commands.is_owner()
    async def setavatar(self, ctx, url: str = None):
        image_url = None
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        elif url:
            image_url = url
        else:
            return await ctx.reply(
                "Please attach an image or provide a URL.\nUsage: `-setavatar <url>` or attach an image.",
                mention_author=False
            )
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await ctx.reply("Failed to download the image. Check the URL and try again.", mention_author=False)
                image_bytes = await resp.read()
                content_type = resp.content_type or "image/png"
        data_uri = f"data:{content_type};base64,{base64.b64encode(image_bytes).decode()}"
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {__import__('os').getenv('TOKEN')}",
                         "Content-Type": "application/json"},
                json={"avatar": data_uri}
            ) as resp:
                if resp.status == 200:
                    embed = discord.Embed(
                        description="<a:green_tick:1103363669263405157> | Bot avatar updated successfully!",
                        color=0x2f3136)
                    embed.set_thumbnail(url=image_url)
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    error = await resp.text()
                    await ctx.reply(f"Discord API error ({resp.status}): {error}", mention_author=False)

    @commands.command(name="setbanner", help="Change the bot's profile banner. Attach an image or provide a URL.")
    @commands.is_owner()
    async def setbanner(self, ctx, url: str = None):
        image_url = None
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        elif url:
            image_url = url
        else:
            return await ctx.reply(
                "Please attach an image or provide a URL.\nUsage: `-setbanner <url>` or attach an image.",
                mention_author=False
            )
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await ctx.reply("Failed to download the image. Check the URL and try again.", mention_author=False)
                image_bytes = await resp.read()
                content_type = resp.content_type or "image/png"
        data_uri = f"data:{content_type};base64,{base64.b64encode(image_bytes).decode()}"
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {__import__('os').getenv('TOKEN')}",
                         "Content-Type": "application/json"},
                json={"banner": data_uri}
            ) as resp:
                if resp.status == 200:
                    embed = discord.Embed(
                        description="<a:green_tick:1103363669263405157> | Bot banner updated successfully!",
                        color=0x2f3136)
                    embed.set_image(url=image_url)
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    error = await resp.text()
                    await ctx.reply(
                        f"Discord API error ({resp.status}): {error}\n\n"
                        "-# Note: Banner updates require the bot to be verified or in a boosted server.",
                        mention_author=False
                    )

    @commands.command()
    @commands.is_owner()
    async def globalban(self, ctx, *, user: discord.User = None):
        if user is None:
            return await ctx.send(
                "You need to define the user"
            )
        for guild in self.client.guilds:
            for member in guild.members:
                if member == user:
                    await user.ban(reason="lund le lo")
               
        
