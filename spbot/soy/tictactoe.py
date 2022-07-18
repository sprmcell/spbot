### uwu i hate myself
import discord
import random
import asyncio
from typing import List, Union
from discord.ext import commands
from discord.ext.commands.core import Command
from bot import Bot




_O: str = ':o2:'
_X: str = ':regional_indicator_x:'
_BLANK: str = ':white_large_square:'


class TicTacToe:
    def __init__(self, player_1: discord.Member, player_2: discord.Member) -> None:
        # private:
        
        self.__player_1: discord.Member = player_1
        self.__player_2: discord.Member = player_2
        self.__running: bool = False

        # public

        self.current_player: discord.Member = random.choice([self.__player_1, self.__player_2])

        self.game_board: list[list[str]] = [
            [_BLANK, _BLANK, _BLANK],
            [_BLANK, _BLANK, _BLANK],
            [_BLANK, _BLANK, _BLANK]
        ]
        self.print_game = lambda: '\n'.join(''.join(line) for line in self.game_board)

        self.player_xo = {self.__player_1: _O, self.__player_2: _X}
        self.player_colour = {self.__player_1: discord.Colour.from_rgb(255, 0, 0), self.__player_2: discord.Colour.blue()}
        self.switch_dict = {self.__player_1: self.__player_2, self.__player_2: self.__player_1}

        self.game_board_message: discord.Message = None
        self.who_turn_message: discord.Message = None
        self.client: Bot = None
        self.move_msgs: list[discord.Message] = []

        self.move_choice = {
            '1️⃣': 0,
            '2️⃣': 1,
            '3️⃣': 2,
            '4️⃣': 3,
            '5️⃣': 4,
            '6️⃣': 5,
            '7️⃣': 6,
            '8️⃣': 7,
            '9️⃣': 8
        }


    def __repr__(self) -> str:
        return str(self.game_board_message.id) 

    # ------------
    # getters/setters
    # ------------

    @property
    def player_1(self) -> discord.Member:
        return self.__player_1


    @property
    def player_2(self) -> discord.Member:
        return self.__player_2

    
    @property
    def running(self) -> bool:
        return self.__running


    @property
    def current_colour(self) -> discord.Colour:
        return self.player_colour[self.current_player]


    @property
    def current_xo(self) -> str:
        return self.player_xo[self.current_player]


    def get_turn_embed(self) -> discord.Embed:
        return discord.Embed(
            colour=self.current_colour
        ).set_author(
            name=self.current_player.display_name + '  -  turn', 
            icon_url=self.current_player.avatar_url
        )


    def switch(self) -> None:
        self.current_player = self.switch_dict[self.current_player]


    def check_if_won(self, player: str, game_board: list[list[str]]=None) -> bool:
        game_board = game_board or self.game_board
        
        # H check
        for line in game_board:
            if ''.join(line) == player * 3:
                return True

        # V check
        for line_idx, _ in enumerate(game_board):
            if ''.join(tuple(map(lambda line: line[line_idx], game_board))) == player * 3:
                return True

        # Size ways check
        if game_board[1][1] == player:
            if game_board[0][0] == player and game_board[2][2] == player:
                return True
            if game_board[0][2] == player and game_board[2][0] == player:
                return True

        return False


    async def _REDO(self):
        new_ttt_game = TicTacToe(self.player_1, self.player_2)
        await new_ttt_game.start(self.client, self.ctx)

    
    async def end_game(self):
        self.__running = False
        
        redo_emoji: str = '🔄'
        await self.who_turn_message.add_reaction(redo_emoji)
        self.client.reactions_add[self.who_turn_message.id] = self.on_redo_reaction_add

        game_msg_id: int = self.game_board_message.id
        del self.client.reactions_add[game_msg_id]

        await TicTacToe.wait_for_again(redo_emoji, self.who_turn_message, self.client)
        
        self.client.running_tictactoe.remove(game_msg_id)


    async def tie_process(self):
        if not self.running:
            return
        embed = discord.Embed(
            title='Tie!'
        )
        asyncio.create_task(
            self.who_turn_message.edit(embed=embed)
        )

        await self.end_game()


    async def win_process(self):
        embed = discord.Embed(
            title='Winner!',
            description=random.choice(self.client.ttt_winner_says),
            colour=discord.Colour.from_rgb(0, 255, 0)
        )
        embed.set_thumbnail(url=self.current_player.avatar_url)
        embed.set_author(name=self.current_player, icon_url=self.current_player.avatar_url)

        asyncio.create_task(
            self.who_turn_message.edit(embed=embed)
        )

        await self.end_game()


    async def didnt_make_a_move(self):
        asyncio.create_task(
            self.who_turn_message.edit(
                embed=discord.Embed(
                    description="%s took to long to make a move, what a NOOB!" % self.current_player.mention
                )
            )
        )


    async def bot_smart_move(self) -> int:
        if not self.current_player.bot:
            return None

        move: int = None
        
        other_player: discord.Member = self.switch_dict[self.current_player]

        for player in [self.current_player, other_player]:
            xo = self.player_xo[player]

            for emoji, idx in self.move_choice.items():
                game_board_copy = [self.game_board[0].copy(), self.game_board[1].copy(), self.game_board[2].copy()] # deep copy
    
                game_board_copy = await self.move(idx, game_board_copy, xo)
                
                # await self.ctx.send(game_board_copy)

                if self.check_if_won(xo, game_board_copy):
                    move = idx
                    return move

        open_corners = [idx for idx in self.move_choice.values() if idx in [0, 2, 6, 8]]

        if len(open_corners) > 0:
            move = random.choice(open_corners)
            return move

        if '5️⃣' in self.move_choice:
            move = self.move_choice['5️⃣']
            return move

        open_endges = [idx for idx in self.move_choice.values() if idx in [1, 3, 5, 7]]

        if len(open_endges) > 0:
            move = random.choice(open_endges)
        
        return move  


    async def update_turn_message(self) -> None:
        await self.who_turn_message.edit(embed=self.get_turn_embed())


    async def delete_move_messages(self):
        if not self.move_msgs:
            return

        for msg in self.move_msgs:
            await msg.delete()
        self.move_msgs.clear()


    async def on_reaction_add(self, payload: discord.RawReactionActionEvent) -> bool:
        if payload.user_id == self.current_player.id:
            try:
                await self.move(self.move_choice[payload.emoji.name])
            except KeyError:
                pass
        
        return False


    async def on_redo_reaction_add(self, payload: discord.RawReactionActionEvent) -> bool:
        if payload.emoji.name != '🔄':
            return
        
        if payload.user_id in [self.player_1.id, self.player_2.id] or (self.player_1.bot and self.player_2.bot):
            self.client.running_tictactoe.remove(self)
            asyncio.create_task(self._REDO())
            return True
        
        return False


    async def add_reactions(self) -> None:
        for emoji in self.move_choice.keys():
            asyncio.create_task(self.game_board_message.add_reaction(emoji))


    async def update_game_board_message(self) -> None:
        await self.game_board_message.edit(content=self.print_game())


    async def move_process(self, move_idx: int) -> None:
        await self.update_game_board_message()

        if self.check_if_won(self.current_xo):
            await self.win_process()
        else:
            self.switch()
            await self.update_turn_message()
            await self.delete_move_messages()

            for emoji in self.move_choice.keys():
                if move_idx == self.move_choice[emoji]:
                    del self.move_choice[emoji]
                    break

            if len(self.move_choice) <= 0:
                return await self.tie_process()

            if self.current_player.bot:
                await self.move(await self.bot_smart_move())


    async def move(self, move_idx: int, game_board: list[list[str]]=None, xo: str=None) -> Union[None, list[list[str]]]:
        if not self.running:
            return

        game_board = game_board or self.game_board
        xo = xo or self.current_xo
        idx = 0

        for x, line in enumerate(game_board):
            for y, block in enumerate(line):
                if idx == move_idx:
                    if not block == _BLANK:
                        return

                    game_board[x][y] = xo

                    if game_board == self.game_board:
                        await self.move_process(move_idx)
                    else:
                        return game_board

                idx += 1


    async def check_if_not_moving(self):
        wait_time: int = 30

        while self.__running:
            game_board_temp = self.print_game()
            await asyncio.sleep(wait_time)
            if game_board_temp == self.print_game():
                self.move_msgs.append(await self.game_board_message.reply("%s make a move!" % self.current_player.mention))
                await asyncio.sleep(wait_time)
                if game_board_temp == self.print_game():
                    await self.didnt_make_a_move()        
                    await self.end_game()


    async def start(self, client: Bot, ctx: commands.Context) -> None:
        self.client = client
        self.ctx = ctx

        self.game_board_message = await ctx.send(self.print_game())

        if not self.player_1.bot or not self.player_2.bot:
            await self.add_reactions()

        self.who_turn_message = await ctx.send(embed=self.get_turn_embed())

        client.running_tictactoe.add(self)
        client.reactions_add[self.game_board_message.id] = self.on_reaction_add

        self.__running = True

        if self.current_player.bot:
            await self.move(await self.bot_smart_move())

        await self.check_if_not_moving()


    @staticmethod
    async def wait_for_again(redo_emoji: str, msg: discord.Message, client: Bot):
        await asyncio.sleep(30)

        try:
            del client.reactions_add[msg.id]
            await msg.remove_reaction(redo_emoji, client.user)
        except KeyError:
            pass


class RunningTicTacToe:
    def __init__(self) -> None:
        self.__running_ttt: dict[str][TicTacToe] = {}


    @property
    def running_ttt(self):
        return self.__running_ttt


    def add(self, ttt: TicTacToe) -> None:
        self.__running_ttt[str(ttt)] = ttt


    def remove(self, id: Union[int, str]) -> None:
        try:
            del self.__running_ttt[str(id)]
        except KeyError:
            pass


    def __getitem__(self, message_id: int) -> TicTacToe:
        return self.__running_ttt[str(message_id)]
