from discord import Intents
from discord.ext import commands

from constants import extensions
from handlers.config_handler import initialize_config

# import logging
# logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    intents = Intents.default()
    intents.members = True

    try:
        from handlers.mediawiki_handler import mediawiki_login
        from config_values import token, prefix

        print("Настройки успешно загружены, загружаю остальное...")
    except KeyError:
        initialize_config()

    bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), case_insensitive=True, intents=intents)
    bot.remove_command('help')
    for extension in extensions:
        bot.load_extension(extension)


    @bot.event
    async def on_ready():
        await mediawiki_login()
        print("Хранитель Лимба запущен и готов к работе.")


    bot.run(token)
