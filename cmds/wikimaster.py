from discord import Embed
from discord.ext import commands

import constants
import handlers.mediawiki_handler as mw
import utility.interactive_util as inter
from lines import *


class WikiMasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='викимастерская')
    @commands.has_any_role(constants.wiki_registrar_role, constants.admin_role)
    @commands.guild_only()
    async def help_for_moderation(self, ctx):
        embed = Embed()
        embed.title = "Команды для вики-мастеров"
        embed.colour = constants.color_codes["Info"]
        embed.title = ""
        embed.description = " "
        embed.add_field(name="!вики-регистрация",
                        value="**Описание:** регистрирует нового пользователя на вики.\n**Формат:** команда, "
                              "имя нового аккаунта, пароль.\n**Пример:**  `!вики-регистрация John qwerty`",
                        inline=False)
        embed.add_field(name="!вики-бан",
                        value="**Описание:** банит пользователя на вики. Все баны через эту команду "
                              "бессрочные.\n**Формат:** команда, имя аккаунта для бана, причина. \n**Пример:**  "
                              "`!вики-бан John вандализм`",
                        inline=False)
        embed.add_field(name="!вики-разбан",
                        value="**Описание:** разбанивает пользователя на вики.\n**Формат:** команда, имя аккаунта для "
                              "разбана, причина.\n**Пример:**  `!вики-разбан John извинился`",
                        inline=False)
        embed.add_field(name="!вики-пароль",
                        value="**Описание:** меняет пароль пользователю.\n**Формат:** команда, имя аккаунта для "
                              "смены, пароль.\n**Пример:**  `!вики-пароль John qwerty123`",
                        inline=False)
        embed.add_field(name="!вики-откат",
                        value="**Описание:** откатывает последние правки пользователя на вики. Работает только на тех "
                              "страницах, последние правки на которых были сделаны откатываемым пользователем, "
                              "т.е. если после него страницы изменял кто-то еще, то они не будут откачены. Откатывает "
                              "вообще все, для более точного отката лучше действовать вручную через "
                              "интерфейс.\n**Формат:** команда, имя аккаунта для отката.\n**Пример:**  `!вики-откат "
                              "John`",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="вики-регистрация")
    @commands.has_any_role(constants.wiki_registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_register(self, ctx, *args):
        username = None
        password = None
        try:
            username = args[0][0]
            password = args[0][1]
        except IndexError:
            pass
        except AttributeError:
            pass

        if not username:
            username = await inter.input_raw_text(self, ctx, wiki_user_tooltip)
        if not password:
            password = await inter.input_raw_text(self, ctx, wiki_password_tooltip)

        result = await mw.create_wiki_account(username, password)
        if result is True:
            await ctx.send("Аккаунт на вики успешно создан.")
        else:
            await ctx.send(
                "Аккаунт на вики создать не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")

    @commands.command(name="вики-бан")
    @commands.has_any_role(constants.wiki_registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_ban(self, ctx, *args):
        username = None
        reason = None
        try:
            username = args[0][0]
            reason = args[0][1]
        except IndexError:
            pass
        except AttributeError:
            pass

        if not username:
            username = await inter.input_raw_text(self, ctx, wiki_user_tooltip)
        if not reason:
            reason = await inter.input_raw_text(self, ctx, wiki_reason_tooltip)

        result = await mw.ban_wiki_account(username, reason)
        if result is True:
            await ctx.send("Аккаунт на вики успешно забанен.")
        else:
            await ctx.send(
                "Аккаунт на вики забанить не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")

    @commands.command(name="вики-разбан")
    @commands.has_any_role(constants.wiki_registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_unban(self, ctx, *args):
        username = None
        reason = None
        try:
            username = args[0][0]
            reason = args[0][1]
        except IndexError:
            pass
        except AttributeError:
            pass

        if not username:
            username = await inter.input_raw_text(self, ctx, wiki_user_tooltip)
        if not reason:
            reason = await inter.input_raw_text(self, ctx, wiki_reason_tooltip)

        result = await mw.unban_wiki_account(username, reason)
        if result is True:
            await ctx.send("Аккаунт на вики успешно разбанен.")
        else:
            await ctx.send(
                "Аккаунт на вики разбанить не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")

    @commands.command(name="вики-пароль")
    @commands.has_any_role(constants.wiki_registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_password(self, ctx, *args):
        username = None
        password = None
        try:
            username = args[0][0]
            password = args[0][1]
        except IndexError:
            pass
        except AttributeError:
            pass

        if not username:
            username = await inter.input_raw_text(self, ctx, wiki_user_tooltip)
        if not password:
            password = await inter.input_raw_text(self, ctx, wiki_password_tooltip)
        result = await mw.change_password(username, password)
        if result.startswith("Password set"):
            await ctx.send("Новый пароль задан. Все в порядке.")
        else:
            await ctx.send("Что-то пошло не так. Сообщение от MediaWiki: " + "```" + result + "```")

    @commands.command(name="вики-откат")
    @commands.has_any_role(constants.wiki_registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_rollback(self, ctx, *args):
        username = None
        try:
            username = args[0][0]
        except IndexError:
            pass
        except AttributeError:
            pass

        if not username:
            username = await inter.input_raw_text(self, ctx, wiki_user_tooltip)

        result = await mw.rollback(username)
        if result.startswith("Processing"):
            await ctx.send(
                "Сам по себе скрипт успешно запустился, дальше пускай MediaWiki скажет сама: " + "```" + result + "```")
        else:
            await ctx.send("Что-то пошло не так. Сообщение от MediaWiki: " + "```" + result + "```")


def setup(bot):
    bot.add_cog(WikiMasterCog(bot))
