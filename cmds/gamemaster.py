from discord import User, Embed
from discord.ext import commands

import config_values
import constants
import handlers.mongo_handler as mng
import handlers.mysql_handler as db
import utility.gamemaster_util as util
import utility.interactive_util as inter
from lines import *


async def del_check_ban_unban(self, ctx, start_text, to_do_with_char, to_do_with_user, *args):
    what = None
    subject = None
    try:
        what = args[0][0]
        subject = args[0][1]
    except (IndexError, AttributeError):
        pass

    what = await inter.one_or_another(self, ctx, start_text, gm_int_what_error, what)
    if what == "персонажа":
        subject = await inter.check_char(self, ctx, gm_int_char_tooltip, gm_int_char_error, subject)
        await to_do_with_char(ctx, subject)
    elif what == "игрока":
        subject = await inter.discord_user_get_id(self, ctx, gm_int_user_tooltip, gm_int_user_error, subject)
        await to_do_with_user(ctx, subject)


class GameMasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='гейммастерская')
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    @commands.guild_only()
    async def help_for_moderation(self, ctx):
        embed = Embed()
        embed.title = "Команды для гейм-мастеров и регистраторов:"
        embed.colour = constants.color_codes["Info"]
        embed.description = "Вводите с осторожностью, перепроверяйте команды и все такое. Непоправимого мало, " \
                            "а вот неприятного и так достаточно. "
        embed.add_field(name=f"{config_values.prefix}зарегистрировать",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              "**Описание:** регистрирует нового персонажа. \n**Формат:** команда, имя персонажа ("
                              "латинница с большой буквы), пароль, затем слап или id или юзернейм игрока, "
                              f"и наконец прямая ссылка на вики \n**Пример:** `{config_values.prefix}"
                              f"зарегистрировать John qwerty @John https://google.com`",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}удалить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              '**Описание:** удаляет персонажа либо игрока. Навсегда.\n**Формат:** команда, '
                              'слово "персонажа" или "игрока", затем соотв-но имя персонажа или имя (можно передать '
                              f'через юзернейм, слап, id) игрока.\n**Пример:**  `{config_values.prefix}'
                              'удалить игрока @John`\n',
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}забанить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              '**Описание:** банит (но не удаляет) игрока в базе данных (не в игре и не в '
                              'дискорде).\n**Формат:** аналогичный с командой "удалить".\n**Пример:**  `'
                              f'{config_values.prefix}забанить персонажа John`\n',
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}разбанить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              '**Описание:** разбанивает одного персонажа или всех персонажей игрока.\n**Формат:** '
                              'аналогичный с командой "удалить"\n**Пример:**  `'
                              f'{config_values.prefix}разбанить игрока John"`\n',
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}проверить",
                        value="**Ввод без аргументов или с их нехваткой активирует интерактивный режим.** \n"
                              "**Описание:** если спрашивают об игроке, выводит всех его забаненных персонажей, "
                              "если о персонаже - пишет, забанен ли он.\n**Формат:** аналогичный с командой "
                              f"'удалить'\n**Пример:**  `{config_values.prefix}проверить игрока John `\n",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}дамп",
                        value=f"**Описание:** Выводит всю инфу обо всех персонажах игрока. id.\n**Формат:** команда, "
                              f"слап, id или юзернейм игрока. \n**Пример:**  `{config_values.prefix}"
                              f"дамп 123412341234123412`\n",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}судо-пароль",
                        value="**Описание:** меняет пароль на персонаже, даже если вы не его владелец.\n**Формат:** "
                              "команда, затем имя персонажа, затем новый пароль.\n**Пример:**  `"
                              f"{config_values.prefix}судо-пароль John qwerty123`\n",
                        inline=False)
        embed.add_field(name=f"{config_values.prefix}банлист",
                        value="**Описание:** выводит всех забаненных.\n**Формат:** команда, без аргументов. "
                              f"\n**Пример:**  `{config_values.prefix}банлист`\n",
                        inline=False)
        await ctx.send(embed=embed)

    # Блок команды регистрации

    @commands.command(name="зарегистрировать")
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
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
        except (IndexError, AttributeError):
            pass

        character = await inter.user_or_pass(self, ctx, 15, gm_int_reg_char_tooltip, gm_int_reg_char_error, character)
        password = await inter.user_or_pass(self, ctx, 15, gm_int_reg_pass_tooltip, gm_int_reg_pass_error, password)
        user_id = await inter.discord_user_get_id(self, ctx, point_on_user, gm_int_reg_user_error, user)
        wiki_link = await inter.input_wiki_link(self, ctx, gm_int_reg_wiki_tooltip, gm_int_reg_wiki_error, wiki_link)
        await util.registration(ctx, character, password, user_id, wiki_link)

    @commands.command(name="удалить")
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_delete(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_del_what_tooltip, util.delete_char, util.delete_user, *args)

    @commands.command(name="забанить")
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_ban(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_ban_what_tooltip, util.ban_char, util.ban_user, *args)

    @commands.command(name="разбанить")
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_unban(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_unban_what_tooltip, util.unban_char, util.unban_user, *args)

    @commands.command(name="проверить")
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    @commands.guild_only()
    @inter.exception_handler_decorator
    async def interactive_check(self, ctx, *args):
        await del_check_ban_unban(self, ctx, gm_int_check_what_tooltip, util.check_char, util.check_user, *args)

    # Неинтерактивные команды

    @commands.command(name="дамп")
    @commands.guild_only()
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
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
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    async def sudo_password_change(self, ctx, character, password):
        result = db.set_new_password(character, password)
        if result == 0:
            await ctx.send("Что-то не так. Может, персонаж неправильно указан?")
        else:
            await ctx.send("Новый пароль задан.")

    @commands.command(name="банлист")
    @commands.guild_only()
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
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

    @commands.command(name="обнулитьперсонажа")
    @commands.guild_only()
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    async def reset_char_stats(self, ctx, char_name):
        discord_user = mng.get({"character": char_name})["discord_user"]
        mng.delete({"character": char_name})
        mng.create_new_character(char_name, discord_user)
        await ctx.send("Персонаж успешно обнулен.")

    @commands.command(name="обнулитьвсехперсонажей")
    @commands.guild_only()
    @commands.has_any_role(config_values.admin_role)
    async def reset_all_char_stats(self, ctx):
        all_chars = mng.get({}, multiple=True)
        for char in all_chars:
            discord_user = char["discord_user"]
            char_name = char["character"]
            mng.delete({"character": char_name})
            mng.create_new_character(char_name, discord_user)
            await ctx.send("Персонаж " + str(char_name) + " успешно пересоздан.")


    @commands.command(name="создатьперсонажа")
    @commands.guild_only()
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    async def create_char_stats(self, ctx, char_name, discord_id):

        user_id = await inter.discord_user_get_id(self, ctx, point_on_user, gm_int_reg_user_error, discord_id)

        mng.create_new_character(char_name, user_id)
        await ctx.send("Персонаж успешно создан.")

    @commands.command(name="удалитьперсонажа")
    @commands.guild_only()
    @commands.has_any_role(config_values.registrar_role, config_values.admin_role)
    async def delete_char_stats(self, ctx, char_name):
        mng.delete({"character": char_name})
        await ctx.send("Персонаж успешно удален.")


def setup(bot):
    bot.add_cog(GameMasterCog(bot))
