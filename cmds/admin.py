from discord.ext import commands

import constants
from bot import initial_extensions


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
