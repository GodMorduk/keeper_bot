import re
from configparser import NoSectionError

from discord import Intents
from discord.ext import commands

from handlers.config_handler import initialize_config

# import logging
# logging.basicConfig(level=logging.DEBUG)

initial_extensions = ['cmds.gamemaster', 'cmds.wikimaster', 'cmds.player', 'cmds.admin', "cmds.fun",
                      'utility.discord_util']

if __name__ == '__main__':

    intents = Intents.default()
    intents.members = True

    try:
        from handlers.mediawiki_handler import mediawiki_login
        from constants import token

        print("Настройки успешно загружены, загружаю остальное...")
    except NoSectionError:
        initialize_config()

    bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), case_insensitive=True, intents=intents)
    bot.remove_command('help')
    for extension in initial_extensions:
        bot.load_extension(extension)


    @bot.event
    async def on_ready():
        await mediawiki_login()
        print("Хранитель Лимба запущен и готов к работе.")


    @bot.listen("on_message")
    async def show_help(msg):
        ctx = await bot.get_context(msg)
        if re.match(f"^<@!?{bot.user.id}>.*", msg.content) and not ctx.valid:
            await ctx.send("Привет. Я бот Галахад. Мои команды можно посмотреть, если сказать мне 'галахад' или "
                           "'команды'.\nМои префиксы (что писать перед командой, чтобы я обратил на тебя внимание): "
                           "это \"!\" или можно меня слапнуть, сопроводив это командой. В случае слапа нужен пробел."
                           "\n**Примеры команд:** `!галахад` или `@галахад команды`.")


    bot.run(token)
