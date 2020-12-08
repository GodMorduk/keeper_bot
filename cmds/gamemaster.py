from discord import User, Embed
from discord.ext import commands

import constants
import handlers.db_handler as db
import utility.gamemaster_util as util
import utility.interactive_util as inter
from lines import *


async def del_check_ban_unban(self, ctx, start_text, to_do_with_char, to_do_with_user, *args):
    what = None
    subject = None
    try:
        what = args[0][0]
        subject = args[0][1]
    except IndexError:
        pass
    except AttributeError:
        pass

    what = await inter.user_or_char(self, ctx, start_text, gm_int_what_error, what)
    if what == "персонажа":
        subject = await inter.check_char(self, ctx, gm_int_char_tooltip, gm_int_char_error, subject)
        await to_do_with_char(ctx, subject)
    elif what == "игрока":
        subject = await inter.discord_user(self, ctx, gm_int_user_tooltip, gm_int_user_error, subject)
        await to_do_with_user(ctx, subject)


class GameMasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='гейммастерская')
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    @commands.guild_only()
    async def help_for_moderation(self, ctx):
        embed = Embed()
        embed.title = "Команды для гейм-мастеров и регистраторов:"
        embed.colour = constants.color_codes["Info"]
        embed.description = "Вводите с осторожностью, перепроверяйте команды и все такое. Непоправимого мало, " \
                            "а вот неприятного и так достаточно. "
        embed.add_field(name="!зарегистрировать",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              "**Описание:** регистрирует нового персонажа. \n**Формат:** команда, имя персонажа ("
                              "латинница с большой буквы), пароль, затем слап или id или юзернейм игрока, "
                              "и наконец прямая ссылка на вики \n**Пример:** `!зарегистрировать John qwerty @John "
                              "https://google.com`",
                        inline=False)
        embed.add_field(name="!удалить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              '**Описание:** удаляет персонажа либо игрока. Навсегда.\n**Формат:** команда, '
                              'слово "персонажа" или "игрока", затем соотв-но имя персонажа или имя (можно передать '
                              'через юзернейм, слап, id) игрока.\n**Пример:**  `!удалить игрока @John`\n',
                        inline=False)
        embed.add_field(name="!забанить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              '**Описание:** банит (но не удаляет) игрока в базе данных (не в игре и не в '
                              'дискорде).\n**Формат:** аналогичный с командой "удалить".\n**Пример:**  `!забанить '
                              'персонажа John`\n',
                        inline=False)
        embed.add_field(name="!разбанить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              '**Описание:** разбанивает одного персонажа или всех персонажей игрока.\n**Формат:** '
                              'аналогичный с командой "удалить"\n**Пример:**  `!разбанить игрока John"`\n',
                        inline=False)
        embed.add_field(name="!проверить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              "**Описание:** если спрашивают об игроке, выводит всех его забаненных персонажей, "
                              "если о персонаже - пишет, забанен ли он.\n**Формат:** аналогичный с командой "
                              "'удалить'\n**Пример:**  `!проверить игрока John `\n",
                        inline=False)
        embed.add_field(name="!дамп",
                        value="**Описание:** Выводит всю инфу обо всех персонажах игрока. id.\n**Формат:** команда, "
                              "слап, id или юзернейм игрока. \n**Пример:**  `!дамп 123412341234123412`\n",
                        inline=False)
        embed.add_field(name="!судо-пароль",
                        value="**Описание:** меняет пароль на персонаже, даже если вы не его владелец.\n**Формат:** "
                              "команда, затем имя персонажа, затем новый пароль.\n**Пример:**  `!судо-пароль John "
                              "qwerty123`\n",
                        inline=False)
        embed.add_field(name="!банлист",
                        value="**Описание:** выводит всех забаненных.\n**Формат:** команда, без аргументов. "
                              "\n**Пример:**  `!банлист qwerty123`\n",
                        inline=False)
        await ctx.send(embed=embed)

    # Блок команды регистрации

    @commands.command(name="зарегистрировать")
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_register(self, ctx, *args):

        character = None
        password = None
        user = None
        wiki_link = None

        try:
            character = args[0][0]
            password = args[0][1]
            user = args[0][2]
            wiki_link = args[0][3]
        except IndexError:
            pass
        except AttributeError:
            pass

        character = await inter.max_len(self, ctx, 15, gm_int_reg_char_tooltip, gm_int_reg_char_error, character)
        password = await inter.max_len(self, ctx, 15, gm_int_reg_password_tooltip, gm_int_reg_password_error, password)
        user = await inter.discord_user(self, ctx, gm_int_reg_user_tooltip, gm_int_reg_user_error, user)
        wiki_link = await inter.max_len(self, ctx, 99, gm_int_reg_wiki_tooltip, gm_int_reg_user_tooltip, wiki_link)

        await util.registration(ctx, character, password, user, wiki_link)

    @commands.command(name="удалить")
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_delete(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_del_what_tooltip, util.delete_char, util.delete_user, *args)

    @commands.command(name="забанить")
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_ban(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_ban_what_tooltip, util.ban_char, util.ban_user, *args)

    @commands.command(name="разбанить")
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_unban(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_unban_what_tooltip, util.unban_char, util.unban_user, *args)

    @commands.command(name="проверить")
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_check(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_check_what_tooltip, util.check_char, util.check_user, *args)

    # Неинтерактивные команды

    @commands.command(name="дамп")
    @commands.guild_only()
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    async def dump(self, ctx, user: User):
        rows = db.get_all_characters_raw(user.id)
        if rows:
            output = "```"
            for row in rows:
                output += (str(row) + "\n")
            output += "```"
            await ctx.send(output)
        else:
            await ctx.send("Пусто. Скорее всего, на этого игрока пока ничего нет или что-то не так вбито.")

    @commands.command(name="судо-пароль")
    @commands.guild_only()
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    async def sudo_password_change(self, ctx, character, password):
        result = db.set_new_password(character, password)
        if result == 0:
            await ctx.send("Что-то не так. Может, персонаж неправильно указан?")
        else:
            await ctx.send("Новый пароль задан.")

    @commands.command(name="банлист")
    @commands.guild_only()
    @commands.has_any_role(constants.registrar_role, constants.admin_role)
    async def ban_list(self, ctx):
        ban_list = db.ban_full_list()
        if ban_list:
            output = ""
            for character in ban_list:
                if ban_list.index(character) == (len(ban_list) - 1):
                    output += (str(character))
                else:
                    output += (str(character) + ", ")
            await ctx.send(output)
        else:
            await ctx.send("В бане пусто. И такое бывает.")


def setup(bot):
    bot.add_cog(GameMasterCog(bot))
