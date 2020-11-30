from discord.ext import commands

from constants import token
from utility.config_handler import initialize_config
from utility.mediawiki_handler import mediawiki_login

# import logging
# logging.basicConfig(level=logging.DEBUG)

initial_extensions = ['cmds.gamemaster', 'cmds.wikimaster', 'cmds.player', 'cmds.admin',
                      'utility.error_discord_handler']

if __name__ == '__main__':
    initialize_config()
    bot = commands.Bot(command_prefix="!")
    for extension in initial_extensions:
        bot.load_extension(extension)


    @bot.event
    async def on_ready():
        await mediawiki_login()
        print("Хранитель Лимба запущен и готов к работе.")


    bot.run(token)
