from discord import Activity, ActivityType, Game
from discord.ext import commands

import constants
from bot import initial_extensions


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role(constants.admin_role)
    @commands.command(name="займись", hidden=True)
    async def change_playing_status(self, ctx, what, subject):
        if what == "игрой":
            await self.bot.change_presence(activity=Game(name=subject))
        # if what == "стримом":
        #     await self.bot.change_presence(activity=ActivityType.streaming(name=subject, url=None))
        if what == "послушай":
            await self.bot.change_presence(activity=Activity(type=ActivityType.listening, name=subject))
        if what == "посмотри":
            await self.bot.change_presence(activity=Activity(type=ActivityType.watching, name=subject))
        if what == "делом":
            await self.bot.change_presence(activity=None)
            await ctx.send("Занимаюсь делом, ладно")

    @commands.has_role(constants.admin_role)
    @commands.command(name='переключитьдебаг', hidden=True)
    async def debug_toggle(self, ctx):
        if constants.log_enable:
            constants.log_enable = False
            await ctx.send("Дебаг выключен.")
        else:
            constants.log_enable = True
            await ctx.send("Дебаг включен.")

    @commands.has_role(constants.admin_role)
    @commands.command(name='вывестимодули', hidden=True)
    async def module_print(self, ctx):
        output = ""
        await ctx.send("Учтите, что я вывожу только те модули, которые указаны по умолчанию. Их может быть больше.")
        for cog in initial_extensions:
            output += "`" + str(cog) + "` "
        await ctx.send(output)

    @commands.has_role(constants.admin_role)
    @commands.command(name='загрузитьмодуль', hidden=True)
    async def module_load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**Ошибка:** {type(e).__name__} - {e}')
        else:
            await ctx.send("Модуль успешно загружен.")

    @commands.has_role(constants.admin_role)
    @commands.command(name='выгрузитьмодуль', hidden=True)
    async def module_unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**Ошибка:** {type(e).__name__} - {e}')
        else:
            await ctx.send("Модуль успешно выгружен.")

    @commands.has_role(constants.admin_role)
    @commands.command(name='перезагрузитьмодуль', hidden=True)
    async def module_reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**Ошибка:** {type(e).__name__} - {e}')
        else:
            await ctx.send("Модуль успешно перезагружен.")


def setup(bot):
    bot.add_cog(AdminCog(bot))
