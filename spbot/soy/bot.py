### This is not a script dont run it by yourself, you will get errors
### Made by:
### sprmcell:
### https://github.com/sprmcell/spbt
### https://sprmcell.repl.co
### Gentaiii:
### https://github.com/YomoTho/

import discord
from discord.ext.commands.errors import MemberNotFound
from var import MyJson
import os
from reference import Reference
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self, command_prefix: str, args: list[str]=None, running_tictactoe=None, **options):
        super().__init__(command_prefix=command_prefix, **options)
        
        # private
        self.__args: list[str] = args or None
        self._default_prefix: str = command_prefix

        # public
        # removed reddit module because: 
        # A) reddit is closed source trannyware
        # B) modules fucks up my internet 

        # yes i know discord is closed sourced chinkware
        self.running_tictactoe = running_tictactoe
        self.reactions_add: dict = {}
        self.reference: Reference = None

        # These are the answers or replies to the 8ball command
        self._8ball_says: list[str] = [
            "No",
            "Yes",
            "Nah",
            "Yuh",
            "Maybe...",
            "Not at all",
            "For sure"
        ]
        # Shit the bot says when a tard wins TTT
        self.ttt_winner_says = [
            "GG", 
            "GG 2 ez",
            "hax",
            "xa4",
            "aimbot"
        ]
        
    # This just helps us grab user info
    def get_member(self, member: str) -> discord.Member:
        try:
            return self.get_user(int(member))
        except ValueError:
            if member.startswith("<@!"):
                return self.get_user(int(member[3:-1]))
        else:
            raise MemberNotFound("**%s**" % member)

    # Functions from here on down are async

    async def on_ready(self):
        self.reference = Reference(self)
        await self.change_presence(activity=discord.Streaming(name="s!help", url="https://discord.gg/QwvcY4uG52"))
        nig = os.system("neofetch")
        print(nig)

    async def on_message(self, message: discord.Message) -> None:
        if not message.content:
            return
        await self.process_commands(message)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.user_id == self.user.id:
            return

        if payload.message_id in self.reactions_add:
            delete = await self.reactions_add[payload.message_id](payload)
            if delete is True:
                del self.reactions_add[payload.message_id]
