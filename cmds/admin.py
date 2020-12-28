from discord import Activity, ActivityType, Game
from discord.ext import commands

import config_values
import constants
import handlers.db_handler as db
from utility.interactive_util import user_converter


def check_admin_ban_decorator(func):
    async def check_admin_ban_wrapper(self, ctx, *args, **kwargs):
        result = db.check_player_ban_by_id(ctx.author.id)
        if result:
            await ctx.send("Ты в админском бане. I can't let you do that.")
            return
        else:
            func_execution = await func(self, ctx, *args, **kwargs)
            return func_execution

    return check_admin_ban_wrapper


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role(config_values.admin_role)
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

    @commands.has_role(config_values.admin_role)
    @commands.command(name='проверитьлогинпароль', hidden=True)
    async def check_user_password(self, ctx, user, password):
        result = db.check_user_password(user, password)
        if result:
            await ctx.send("Есть совпадение.")
        else:
            await ctx.send("Нет совпадения.")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='переключитьдебаг', hidden=True)
    async def debug_toggle(self, ctx):
        if config_values.log_enable:
            config_values.log_enable = False
            await ctx.send("Дебаг выключен.")
        else:
            config_values.log_enable = True
            await ctx.send("Дебаг включен.")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='вывестимодули', hidden=True)
    async def module_print(self, ctx):
        output = ""
        await ctx.send("Учтите, что я вывожу только те модули, которые указаны по умолчанию. Их может быть больше.")
        for cog in constants.extensions:
            output += "`" + str(cog) + "` "
        await ctx.send(output)

    @commands.has_role(config_values.admin_role)
    @commands.command(name='загрузитьмодуль', hidden=True)
    async def module_load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**Ошибка:** {type(e).__name__} - {e}')
        else:
            await ctx.send("Модуль успешно загружен.")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='выгрузитьмодуль', hidden=True)
    async def module_unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**Ошибка:** {type(e).__name__} - {e}')
        else:
            await ctx.send("Модуль успешно выгружен.")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='перезагрузитьмодуль', hidden=True)
    async def module_reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**Ошибка:** {type(e).__name__} - {e}')
        else:
            await ctx.send("Модуль успешно перезагружен.")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='админскийбан', hidden=True)
    @check_admin_ban_decorator
    async def admin_ban(self, ctx, user):
        subject = await user_converter.convert(ctx, user)

        if subject.id == config_values.owner_id:
            await ctx.send("Its a treason, then. Баню тебя самого.")
            subject = ctx.message.author

        result = db.ban_player_by_id(subject.id)

        if not result:
            await ctx.send("Что-то пошло не так. Возможно, он уже забанен?")
        else:
            await ctx.send("Админский бан сказал свое слово.")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='админскийразбан', hidden=True)
    @check_admin_ban_decorator
    async def admin_unban(self, ctx, user):
        subject = await user_converter.convert(ctx, user)
        result = db.unban_player_by_id(subject.id)
        if result:
            await ctx.send("Админский бан снят.")
        else:
            await ctx.send("Что-то пошло не так. Может, он не забанен?")

    @commands.has_role(config_values.admin_role)
    @commands.command(name='админскаяпроверка', hidden=True)
    @check_admin_ban_decorator
    async def admin_check(self, ctx, user):
        subject = await user_converter.convert(ctx, user)
        result = db.check_player_ban_by_id(subject.id)
        if result:
            await ctx.send("Да, он забанен админским баном.")
        else:
            await ctx.send("Нет, он не забанен админским баном.")


def setup(bot):
    bot.add_cog(AdminCog(bot))
