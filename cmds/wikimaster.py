from discord import Embed
from discord.ext import commands

import config_values
import constants
import handlers.db_handler as db
import handlers.mediawiki_handler as mw
import utility.interactive_util as inter
from lines import *


class WikiMasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='викимастерская')
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    async def help_for_moderation(self, ctx):
        embed = Embed()
        embed.title = "Команды для вики-мастеров"
        embed.colour = constants.color_codes["Info"]
        embed.title = ""
        embed.description = " "
        embed.add_field(name=f"{config_values.prefix}вики-регистрация",
                        value="**Описание:** регистрирует нового пользователя на вики.\n**Формат:** команда, "
                              f"имя нового аккаунта, пароль.\n**Пример:**  `{config_values.prefix}"
                              "вики-регистрация John qwerty`",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}вики-бан",
                        value="**Описание:** банит пользователя на вики. Все баны через эту команду "
                              "бессрочные.\n**Формат:** команда, имя аккаунта для бана, причина. \n**Пример:**  "
                              f"`{config_values.prefix}вики-бан John вандализм`",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}вики-разбан",
                        value="**Описание:** разбанивает пользователя на вики.\n**Формат:** команда, имя аккаунта для "
                              f"разбана, причина.\n**Пример:**  `{config_values.prefix}вики-разбан John извинился`",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}вики-пароль",
                        value="**Описание:** меняет пароль пользователю.\n**Формат:** команда, имя аккаунта для "
                              f"смены, пароль.\n**Пример:**  `{config_values.prefix}вики-пароль John qwerty123`",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}вики-откат",
                        value="**Описание:** откатывает последние правки пользователя на вики. Работает только на тех "
                              "страницах, последние правки на которых были сделаны откатываемым пользователем, "
                              "т.е. если после него страницы изменял кто-то еще, то они не будут откачены. Откатывает "
                              "вообще все, для более точного отката лучше действовать вручную через "
                              "интерфейс.\n**Формат:** команда, имя аккаунта для отката.\n**Пример:**  `"
                              f"{config_values.prefix}вики-откат John`",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="вики-релог")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    async def wiki_relog(self, ctx):
        await mw.mediawiki_login()
        await ctx.send("Я перелогинился на вики. Надеюсь это поможет.")

    @commands.command(name="вики-регистрация")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_register(self, ctx, *args):
        username = None
        password = None
        user = None
        try:
            username = args[0][0]
            password = args[0][1]
            user = args[0][2]
        except IndexError:
            pass
        except AttributeError:
            pass

        username = await inter.user_or_pass(self, ctx, 50, wiki_user_tooltip, forbidden_chars, username)
        password = await inter.user_or_pass(self, ctx, 50, wiki_password_tooltip, forbidden_chars, password)
        discord_id = await inter.discord_user_get_id(self, ctx, wiki_registration_tooltip, wiki_registration_error, user)

        try:
            db.get_if_age_confirmed(discord_id)
        except db.AgeNotConfirmed:
            await ctx.send("Игрок не подтвердил возраст. Регистрация отменена.")
        else:
            result = await mw.create_wiki_account(username, password)
            if result is True:
                await ctx.send("Аккаунт на вики успешно создан.")
                db.add_new_wiki_account(username, discord_id)
            else:
                await ctx.send(
                    "Аккаунт на вики создать не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result +
                    "```")

    @commands.command(name="вики-бан")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_ban(self, ctx, *args):
        username = None
        reason = None
        try:
            username = args[0][0]
            reason = args[0][1]
        except (IndexError, AttributeError):
            pass

        username = await inter.user_or_pass(self, ctx, 50, wiki_user_tooltip, forbidden_chars, username)
        reason = await inter.input_raw_text_no_checks(self, ctx, wiki_reason_tooltip, reason)

        result = await mw.ban_wiki_account(username, reason)
        if result is True:
            await ctx.send("Аккаунт на вики успешно забанен.")
        else:
            await ctx.send(
                "Аккаунт на вики забанить не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")

    @commands.command(name="вики-разбан")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_unban(self, ctx, *args):
        username = None
        try:
            username = args[0][0]
        except (IndexError, AttributeError):
            pass

        username = await inter.user_or_pass(self, ctx, 50, wiki_user_tooltip, forbidden_chars, username)

        result = await mw.unban_wiki_account(username)
        if result is True:
            await ctx.send("Аккаунт на вики успешно разбанен.")
        else:
            await ctx.send(
                "Аккаунт на вики разбанить не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result +
                "```")

    @commands.command(name="вики-проверка")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_check(self, ctx, *args):
        what = None
        subject = None
        try:
            what = args[0][0]
            subject = args[0][1]
        except (IndexError, AttributeError):
            pass

        what = await inter.one_or_another(self, ctx, wiki_check_tooltip, wiki_check_tooltip, what, "аккаунта")

        if what == "аккаунта":
            subject = await inter.user_or_pass(self, ctx, 50, wiki_user_tooltip, forbidden_chars, subject)
            result = db.check_owner_of_wiki_account(subject)
            if result is None:
                await ctx.send("У меня нет информации по этому аккаунту. Это какая-то ошибка.")
            else:
                await ctx.send(f"Владелец аккаунта {subject} это <@{result}>.")

        elif what == "игрока":
            subject = await inter.discord_user_get_id(self, ctx, gm_int_user_tooltip, gm_int_user_error, subject)
            result = db.check_all_accounts_by_owner(subject)
            if not result:
                await ctx.send(f"У <@{subject}> нет аккаунтов на вики.")
            else:
                output = ""
                for character in result:
                    output += (str(character))
                    if result.index(character) != (len(result) - 1):
                        output += (str(character) + ", ")
                await ctx.send(f"У <@{subject}> следующие аккаунты на вики: " + output)

    @commands.command(name="вики-пароль")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_password(self, ctx, *args):
        username = None
        password = None
        try:
            username = args[0][0]
            password = args[0][1]
        except (IndexError, AttributeError):
            pass

        username = await inter.user_or_pass(self, ctx, 50, wiki_user_tooltip, forbidden_chars, username)
        password = await inter.user_or_pass(self, ctx, 50, wiki_password_tooltip, forbidden_chars, password)

        result = await mw.change_password(username, password)
        if result.startswith("Password set"):
            await ctx.send("Новый пароль задан. Все в порядке.")
        else:
            await ctx.send("Что-то пошло не так. Сообщение от MediaWiki: " + "```" + result + "```")

    @commands.command(name="вики-откат")
    @commands.has_any_role(config_values.wiki_registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def wiki_rollback(self, ctx, *args):
        username = None
        try:
            username = args[0][0]
        except (IndexError, AttributeError):
            pass

        username = await inter.user_or_pass(self, ctx, 50, wiki_user_tooltip, forbidden_chars, username)

        result = await mw.rollback(username)
        if result.startswith("Processing"):
            await ctx.send(
                "Сам по себе скрипт успешно запустился, дальше пускай MediaWiki скажет сама: " + "```" + result + "```")
        else:
            await ctx.send("Что-то пошло не так. Сообщение от MediaWiki: " + "```" + result + "```")


def setup(bot):
    bot.add_cog(WikiMasterCog(bot))
