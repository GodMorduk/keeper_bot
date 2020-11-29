from discord.ext import commands

from utility.config_handler import initialize_config
from utility.mediawiki_handler import mediawiki_login
from constants import token

# import logging
# logging.basicConfig(level=logging.DEBUG)

initialize_config()

bot = commands.Bot(command_prefix="!")

initial_extensions = ['cmds.gamemaster', 'cmds.wikimaster', 'cmds.player',
                      'utility.error_discord_handler']
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    await mediawiki_login()
    print("Хранитель Лимба запущен и готов к работе.")


bot.run(token)
