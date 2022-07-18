"""
This is a script file, should be executed


Author: SasumaTho
Discord: SasumaTho#9999

Status: Done. Might be changed in the future.

"""

import discord
import os
import sys
from dotenv import load_dotenv
from bot import Bot
from tictactoe import RunningTicTacToe

PREFIX='s!'


def main(args: list[str]) -> None:
    """ | Enter point |
    
    Paremters
    ---------

    args: :class:`list[str]`
        This should be `sys.argv`

    
    Returns:
        None

    """

    client = Bot(
        command_prefix=PREFIX,
        args=args,
        running_tictactoe=RunningTicTacToe(),
        case_insensitive=True,
        intents=discord.Intents().all()
    )
    
    client.load_extension('commands') # This is for 'loading the bot commands'

    load_dotenv()

    client.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main(sys.argv[1:])
