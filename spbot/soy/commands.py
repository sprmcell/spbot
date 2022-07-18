### This is all our sexy commands, once again this isnt a script file, dont import it
### I use gb keyboard so this is just to make things easier
### \

import asyncio
from discord import Spotify
from datetime import datetime
from operator import add
from types import FunctionType
from typing import OrderedDict, Union
from asyncio.tasks import create_task
import discord
import sys
import time
import inspect
import os
import random
from discord.ext.commands.core import command
from discord.ext.commands.errors import MemberNotFound
from discord import colour
from bot import Bot 
from discord.ext import commands
from tictactoe import TicTacToe
from var import MyJson


# This is used to @ decorate a functions

commands_classes: list[commands.Cog] = []

def add_class(cls: commands.Cog) -> commands.Cog:

    commands_classes.append(cls)

    return cls

async def command_success(message: Union[discord.Message, commands.Context]) -> None:
    if isinstance(message, commands.Context):
        message: discord.Message = message.message

    await message.add_reaction('✅')

# These are commands the bot owner can run

@add_class
class Owner(commands.Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        await ctx.send("`$ restarting bot...`")
        os.system("clear")
        os.execv(sys.executable, ["python"] + sys.argv)
        await ctx.send("`$ this is the moment Walter became Heisenberg`")

    @commands.command()
    @commands.is_owner()
    async def test(self, ctx: commands.Context):
        sex = os.system("uptime")
        await ctx.send("Test command UwU")
        await ctx.send(sex)

    @commands.command()
    @commands.is_owner()
    async def reboot(self, ctx: commands.Context):
        await ctx.send("Add a feature to run discord bots on boot")
        await ctx.send("Rebooting...")
        os.system("sudo reboot")

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        await ctx.send("Syncing System with the repos...")
        os.system("sudo pacman -Syu --noconfirm")
        await ctx.send("Done, some updates require a reboot")

# Moderation commands

@add_class
class Mod(commands.Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str=None) -> None:
        if member == None or member == ctx.author:
            await ctx.send(f"`Usage:`\n`kick <user> <reason>`\n`Reason is optional`")
        if reason == None:
            reason = "No reason provided"
        await ctx.send(f"`$ kicking {member}...`")
        await member.send(f"`$ you have been kicked from...`\n`$ {ctx.guild.name}`\n`$ reasoning...`\n`$ {reason}`")
        await member.kick(reason=reason)
        await ctx.send(f"`$ kicked {member}... [ ok ]`")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str=None) -> None:
        if member == None or member == ctx.author:
            await ctx.send(f"`Usage:`\n`ban <user> <reason>`\n`Reason is optional`")
        if reason == None:
            reason = "No reason provided"
        await ctx.send(f"`$ banning {member}...`")
        await member.send(f"`$ you have been banned from...`\n`$ {ctx.guild.name}`\n`$ reasoning...`\n`$ {reason}`")
        await member.ban(reason=reason)
        await ctx.send(f"`$ banned {member}... [ ok ]`")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx: commands.Context, member_id: int, *, reason: str=None):
        guild: discord.Guild = ctx.guild

        user = self.client.get_user(member_id)

        await guild.unban(user, reason=reason)

        await ctx.send(f"`$ unbanned {user}... [ ok ]`")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bans(self, ctx: commands.Context):
        embed = discord.Embed(title='Banned members', colour=0x18191c)

        server: discord.Guild = ctx.guild

        banned_members: list[discord.guild.BanEntry] = await server.bans()

        embed.description = '\n'.join(
            ['%s ID: **%i**, Reason: **%s**' % (ban_entry.user.mention, ban_entry.user.id, ban_entry.reason) for ban_entry in banned_members]
        ) if len(banned_members) != 0 else "`$ no banned members to list`\n`$ dont histate to ban someone`"

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx: commands.Context, new_prefix: str) -> None:
        guild_id: str = str(ctx.guild.id)

        with MyJson.readwrite('prefixes.json') as p:
            p[guild_id] = new_prefix

        await ctx.reply("`$ new prefix: %s`" % await self.client.get_prefix(ctx.message))


@add_class
class Nerd(commands.Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client


    # Not a command, used for `code` command
    async def command_code(self, function_name: str) -> Union[discord.File, None]:
        try:
            cmd_function: FunctionType = self.client.all_commands[function_name].callback
        except KeyError:
            return None
        else:
            source_code: str = inspect.getsource(cmd_function)
                
            with open('source_code.py', 'w') as f:
                f.write(source_code)

            file = discord.File('source_code.py')

            return file


    # Not a command, used for `code` command
    async def client_code(self, function_name: str) -> Union[discord.File, None]:
        try:
            func: FunctionType = self.client.__getattribute__(function_name)
        except AttributeError as e:
            return None
        else:
            source_code: str = inspect.getsource(func)

            with open('source_code.py', 'w') as f:
                f.write(source_code)

            file = discord.File('source_code.py')

            return file


    @commands.command()
    async def source(self, ctx: commands.Context, function_name: str) -> None:
        file: discord.File = await self.command_code(function_name) or await self.client_code(function_name)

        if file is None:
            return await ctx.send("`$ ERROR: function '%s' does not exist, for full source code use the 'schizo` command" % function_name)

        await ctx.reply("`$ source code for '%s':`" % function_name)
        await ctx.send(file=file)

        with open('source_code.py', 'w'): pass

    @commands.command()
    async def schizo(self, ctx: commands.Context):
        print("schizo asked for the source code, he gonna see all the data we sell")
        await ctx.send("`$ discord already sells ur data and spies on you, why cant we?`\n`$ lmao kidding babe`\n`$ github`\n`https://github.com/sprmcell/spbot`\n`$ grr but microsoft!1!111!!!`\n`https://gitlab.com/sprmcell/spbot`")

    @commands.command()
    async def lines(self, ctx: commands.Context) -> None:
        lines_of_code: int = 0

        for file in os.scandir('soy/'):
            if file.name.endswith('.py'):
                with open(file) as f:
                    lines_of_code += len(f.readlines())

        await ctx.send(
            embed=discord.Embed(
                description='`$ scanning /home/sp/spbot/ for python code... [ ok ]`\n`$ found %s lines of python code' % lines_of_code,
                colour=0x18191c
            )
        )

    @commands.command()
    async def based(self, ctx: commands.Context, user: discord.Member=None):
        user = discord.Member = user or ctx.author

        bs = random.randint(1, 10)
        embed=discord.Embed(
                title="our team carefully analysed this",
                description=f"lets see how based you really are\n{bs}/10\n\nIf you have any issues, please kys"
                )
        await ctx.reply(embed=embed)


@add_class
class User(commands.Cog):
    def __init__(self, client: Bot) -> None:
        self.client: Bot = client
    
    @commands.command()
    async def poll(self, ctx: commands.Context, option1:str, option2:str, *, question):
        embed=discord.Embed(title=f"{question}", description=f":one: {option1}\n:two: {option2}")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")

    @commands.command()
    async def op(self, ctx: commands.Context):
        nihil = random.choice(["go get em coon", "cry about it"])
        await ctx.send(nihil)

    @commands.command(aliases=["say"])
    async def echo(self, ctx: commands.Context, *, agrs):
        await ctx.message.delete()
        await ctx.send(agrs)

    @commands.command(help="cleans up the servers terminal")
    async def clr(self, ctx: commands.Context):
        await ctx.send("thank you for cleaning the terminal, this coon <@!910905312830165003> never does it")
        os.system("clear")

    @commands.command(aliases=["spotify"], help="spotify uwu")
    async def sp(self, ctx: commands.Context, user: discord.Member = None):
        if user == None:
            user = ctx.author
            pass
        if user.activities:
            for activity in user.activities:
                if isinstance(activity, Spotify):
                    embed = discord.Embed(
                            title = f"{user.name} is currently listening to:",
                            description = f"{activity.title}",
                            colour = 0x1DB954)
                    embed.set_thumbnail(url=activity.album_cover_url)
                    embed.add_field(name="By:", value=activity.artist)
                    embed.add_field(name="On:", value=activity.album)
                    await ctx.send(embed=embed)

    @commands.command(aliases=['av'], help='shows the users avatar')
    async def pfp(self, ctx: commands.Context, member: discord.Member=None) -> None:
        member: discord.Member = member or ctx.author

        avatar_url = member.avatar_url

        embed = discord.Embed(colour=0x18191c)
        embed.set_image(url=avatar_url)
        embed.set_author(name=member.display_name, icon_url=avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def status(self, ctx: commands.Context, member: Union[discord.Member, str]=None, args=None) -> None:
        if isinstance(member, str):
            args = member
            member = ctx.author
        
        def get_nice_type(_type):
            return str(_type[0][0].upper() + _type[0][1:])


        status_icon = {
            'online': 'https://emoji.gg/assets/emoji/9166_online.png',
            'dnd': 'https://emoji.gg/assets/emoji/7907_DND.png',
            'offline': 'https://emoji.gg/assets/emoji/7445_status_offline.png',
            'idle': 'https://i.redd.it/kp69do60js151.png'
        }

        member = member or ctx.author
        _status = member.status

        status_platform = member._client_status.copy()

        del status_platform[None]

        if str(_status) == 'dnd':
            _status = 'Do Not Disturb'

        _status = '%s  -  %s' % (_status, ', '.join(list(status_platform)))

        activities = member.activities

        embed = discord.Embed(colour=0x18191c)
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=_status, icon_url=status_icon[str(member.status)])

        if args == '-a':
            status = []

            for act in activities:
                # TODO: Clean up code

                if str(type(act)) == "<class 'discord.activity.Activity'>":
                    details = ''
                    if act.details is not None:
                        details = '\n> %s\n> %s\n%s' % (act.details, act.state, act.url or '')

                    status.append("%s **%s**%s" % (get_nice_type(act.type), act.name, details))
                elif str(type(act)) == "<class 'discord.activity.Spotify'>": # The user is playing spotify
                    embed.set_thumbnail(url=act.album_cover_url)
                    status.append("%s\n> **%s** - by __%s__\n> on __%s__" % ('%s To %s' % (get_nice_type(act.type), act), act.title, ', '.join(act.artists), act.album))
                else:
                    status.append('%s **%s**' % (get_nice_type(act.type), act))

            status = '\n'.join(status)

            embed.description = status
        elif args == '-d':
            embed.description = str(activities)
            embed.set_footer(text=str(member._client_status))
        else:
            if not len(activities) == 0:
                _type = get_nice_type(activities[0].type)
                _game = activities[0].name

                if not _type == "Playing":
                    if not activities[0].emoji is None:
                        _game = "%s %s" % (activities[0].emoji, _game)

                embed.description="%s **%s**" % (_type, _game)

        await ctx.send(embed=embed)

    @commands.command()
    async def print(self, ctx: commands.Context, *, args):
        print(args)
        await ctx.send("just got done printing your racial slurs in the terminal")

    @commands.command()
    async def whois(self, ctx: commands.Context, member: discord.Member=None) -> None:
        member: discord.Member = member or ctx.author

        member_created_at: datetime = member.created_at
        nick: str = member.nick

        created = member_created_at.strftime(f"%A, %B %d %Y @ %H:%M %p")
        joined = member.joined_at.strftime(f"%A, %B %d %Y @ %H:%M %p")

        embed = discord.Embed(
            title=member,
            description=str("AKA: **`%s`**" % nick if nick else '') + "\n%s" % member.mention,
            color=0x18191c
        )
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(name='Account Creation', value='> `%s`' % created, inline=False)
        embed.add_field(name='Server Joined', value='> `%s`' % joined, inline=False)
        embed.add_field(name='Account Age', value='> `%s`' % (datetime.today() - member_created_at), inline=False)
        embed.add_field(name='Is Admin', value='`%s`' % member.guild_permissions.administrator)
        embed.add_field(name='Is Bot', value='`%s`' % member.bot)
        embed.add_field(name='ID', value='`%i`' % member.id)

        await ctx.send(embed=embed)

    @commands.command()
    async def kiss(self, ctx: commands.Context, member: discord.Member) -> None:
        author: discord.Member = ctx.author

        await ctx.send(f"aww, {author.display_name} gave {member.display_name}, a kiss :heart:")

@add_class
class Fun(commands.Cog):
    def __init__(self, client: Bot) -> None:
        self.client: Bot = client

    @commands.command()
    async def rr(self, ctx: commands.Context):
        rr = random.choice(["* click * you survive another round", "* clack * you live to see another round", ":bang: brains all over the place, collect the bets and clean the walls"])
        await ctx.reply(rr)

    @commands.command(name='8ball')
    async def _8ball(self, ctx: commands.Context, *, question: str):
        embed = discord.Embed(
            title=":8ball: 8ball",
            description=random.choice(self.client._8ball_says), 
            colour=0x18191c)

        await ctx.reply(embed=embed)


    @commands.command(aliases=['ttt', 'tic-tac-toe'])
    async def tictactoe(self, ctx: commands.Context, player1: Union[discord.Member, str], player2: discord.Member=None):
        player2: discord.Member = player2 or ctx.author

        if player1 == player2:
            return await ctx.reply("`$ loner, you cant play alone, you can play with the bot tho`")
        
        print(player1.name, 'vs.', player2.name)

        ttt_game = TicTacToe(player1, player2)
        await ttt_game.start(self.client, ctx)

@add_class
class Misc(commands.Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.reply(
            embed=discord.Embed(
                title="Pinged `162.159.135.232`... [ ok ]",
                description="$ response time:`%i`ms" % round(self.client.latency * 1000),
                colour=0x18191c
            )
        )

    @commands.command()
    async def website(self, ctx: commands.Context):
        await ctx.send("https://sprmcell.repl.co")

    @commands.command()
    async def invite(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                title='NOO ANON DONT CLICK EMBED LINKS!!!',
                description="$ embed to add to your server, theres also a button on the bot's profile",
                url='https://discord.com/api/oauth2/authorize?client_id=913148615118176256&permissions=8&scope=bot',
                colour=0x18191c
            )
        )

def setup(client: commands.Bot) -> None:
    for cmd_cls in commands_classes:
        client.add_cog(cmd_cls(client))
        print('$ added class:', cmd_cls.__name__)
