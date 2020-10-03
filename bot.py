from discord.ext import commands

from constants import token
from utility.config_handler import initialize_config

# import logging
# logging.basicConfig(level=logging.DEBUG)

initialize_config()

initial_extensions = ['cmds.gamemaster', 'cmds.wikimaster', 'cmds.player',
                      'utility.error_discord_handler']

bot = commands.Bot(command_prefix="!")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
