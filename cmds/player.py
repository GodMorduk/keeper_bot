from discord import User, Embed, File
from discord.ext import commands

import constants
import handlers.mongo_handler as mng
import handlers.mysql_handler as db
import utility.interactive_util as inter
import utility.mongo_util as mng_util
import utility.password_util as pswd
import utility.player_util as util
from cmds.admin import check_admin_ban_decorator
from config_values import prefix, dir_launcher, launcher_name, bot_name, bot_genitive_name, registrar_role, admin_role, \
    age_confirmation_categories
from lines import *
from utility.discord_util import user_converter


def count_learning_cost(already_learned):
    tens = already_learned // 10
    numbers = already_learned % 10
    price = 0

    if tens > 0:
        for i in range(tens):
            price += 10 * (i + 1)
        price += numbers * (tens + 1)
        return price
    else:
        return numbers


def count_price(now, need):
    total_price = 0

    for i in range(now + 1, need + 1):
        tens = i // 10
        numbers = i % 10
        if numbers == 0:
            tens -= 1

        if tens < 1:
            total_price += 1
        else:
            total_price += (tens + 1)

    return total_price


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[f'{bot_name}', 'команды'])
    async def help_for_players(self, ctx):
        embed = Embed()
        embed.title = f"Обычные команды {bot_genitive_name}"
        embed.colour = constants.color_codes["Info"]
        embed.description = "Да-да? Тут перечислены все мои команды для обычных игроков. Я, если что, не настоящий " \
                            f"{bot_name}, а всего-лишь бот. "
        embed.add_field(name=f"{prefix}подтвердитьвозраст",
                        value="**Описание:** интерактивная команда. Нужно сделать один раз для каждого пользователя. "
                              f"id.\n**Пример:**  `{prefix}подтвердитьвозраст`",
                        inline=False)
        embed.add_field(name=f"{prefix}персонажи",
                        value="**Описание:** выводит всех персонажей указанного игрока.\n**Формат:** команда, "
                              "затем слапнутый игрок. Можно писать его имя пользователя (не ник) или его "
                              f"id.\n**Пример:**  `{prefix}персонажи @John`",
                        inline=False)
        embed.add_field(name=f"{prefix}викиигрока",
                        value="**Описание:** дает вики-ссылки на всех персонажей игрока.\n**Формат:** команда, "
                              f"затем аналогично пункту выше.\n**Пример:**  `{prefix}викиигрока @John`",
                        inline=False)
        embed.add_field(name=f"{prefix}википерса",
                        value="**Описание:** дает вики-ссылку на конкретного персонажа. Имя персонажа должно быть на "
                              f"латиннице.\n**Формат:** команда, затем имя персонажа\n**Пример:**  `{prefix}википерса "
                              f"John`",
                        inline=False)
        embed.add_field(name=f"{prefix}пароль",
                        value="**Описание:** позволяет сменить пароль. Работает только в личке.\n**Формат:** команда, "
                              f"затем имя персонажа, затем новый пароль.\n**Пример:**  `{prefix}пароль John q1w2e3`",
                        inline=False)
        embed.add_field(name=f"{prefix}лаунчер",
                        value="**Описание:** скидывает вам лаунчер в формате exe. Jar доступен у администрации. "
                              f"Работает только в личке.\n**Формат:** команда\n**Пример:**  `{prefix}лаунчер`",
                        inline=False)
        embed.add_field(name=f"{prefix}скин или {prefix}скины",
                        value="**Описание:** интерактивная команда. Работает только в личке. Весь массив операций со "
                              "скинами, будь это их удаление, добавление и пр.\n**Формат:** "
                              'подсказывается по ходу, но можно забивать аргументы "наперед". Сначала указывается '
                              'действие (залить, получить ссылку, вывести все, получить все ссылки, уничтожить) затем '
                              'строго контекстуально. Если это заливание, то нужно указать имя персонажа, затем '
                              'постфикс, ("Нет" считается отсутствием постфикса), затем нужно приложить пост с файлом. '
                              'Как уже было сказано, можно миксовать как угодно, например заранее написать '
                              f'**{prefix}скин залить Vasya armor** а следующим сообщением залить файл. А можно сразу '
                              f'все. А можно просто **{prefix}скин залить Vasya**, а потом указать постфикс и '
                              f'отправить сообщение со скином.\n**Пример:** `{prefix}скин`',
                        inline=False)
        embed.add_field(name=f"{prefix}персонаж",
                        value="**Описание:** выводит всю информацию о персонаже. "
                              f"\n**Формат:** команда, затем имя персонажа\n"
                              f"**Пример:**  `{prefix}персонаж John`",
                        inline=False)
        embed.add_field(name=f"{prefix}параметры",
                        value="**Описание:** выводит все возможные опции для персонажа."
                              f"\n**Формат:** команда\n**Пример:**  `{prefix}параметры`",
                        inline=False)
        embed.add_field(name=f"{prefix}статы",
                        value="**Описание:** интерактивная команда. Вбейте ее и делайте согласно подсказкам. Можно "
                              "вбивать сразу полностью, если вы и так знаете, что писать."
                              f"\n**Формат:** команда\n**Пример:**  `{prefix}статы`",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="подтвердитьвозраст")
    @commands.guild_only()
    @commands.cooldown(1, 86400.0, commands.BucketType.user)
    @inter.exception_handler_decorator
    @check_admin_ban_decorator
    async def age_confirmation(self, ctx, *args):

        try:
            category_id = str(ctx.channel.category.id)
        except AttributeError:
            category_id = None

        if category_id not in age_confirmation_categories:
            await ctx.send("Не-а. Это можно делать только в тикетах реги (на вики или внутри игры), больше нигде.")

        else:
            try:
                current_state = db.get_if_age_confirmed(ctx.message.author.id)
            except db.AgeNotConfirmed:
                current_state = False

            if current_state:
                await ctx.send(plr_age_confirmation_already)
                ctx.command.reset_cooldown(ctx)
            else:
                result = await inter.age_confirmation(self, ctx)
                if result is True:
                    db.confirm_age(ctx.message.author.id)
                    await ctx.send("Возраст подтвержден. Хорошей игры.")
                    ctx.command.reset_cooldown(ctx)
                else:
                    await ctx.send("Не удалось подтвердить возраст. Не подтверждаю.")

    @commands.command(name="персонажи")
    @commands.guild_only()
    async def get_characters(self, ctx, user: User = None):
        if not user:
            user = ctx.message.author
        list_of_characters = db.get_all_characters_normal(user.id)
        if not list_of_characters:
            await ctx.send("А персонажей-то и нет.")
        else:
            output = ""
            for character in list_of_characters:
                output += (str(character))
                if list_of_characters.index(character) != (len(list_of_characters) - 1):
                    output += ", "
            await ctx.send(output)

    @commands.command(name="игрок")
    @commands.guild_only()
    async def get_player(self, ctx, character):
        list_of_characters = db.get_player(character)
        if not list_of_characters:
            await ctx.send("Пусто. Что-то не так вбито или такого персонажа нет.")
        else:
            user = await user_converter.convert(ctx, list_of_characters[0])
            await ctx.send(f"Владелец этого персонажа - {user}")

    @commands.command(name="википерса")
    @commands.guild_only()
    async def wiki_char(self, ctx, character):
        output = db.get_character_link(character)
        await ctx.send(output)

    @commands.command(name="викиигрока")
    @commands.guild_only()
    @commands.cooldown(1, 15.0, commands.BucketType.default)
    async def wiki_players(self, ctx, user: User = None):
        if not user:
            user = ctx.message.author
        list_of_characters = db.get_all_characters_links(user.id)
        output = ""
        for link in list_of_characters:
            output += (str(link) + "\n")
        await ctx.send(output)

    @commands.command(name="пароль")
    @commands.dm_only()
    async def password_change(self, ctx, character, password):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            db.set_new_password(character, password)
            await ctx.send("Новый пароль задан.")
        else:
            await ctx.send("У тебя нет такого персонажа. Что-то тут не так.")

    @commands.command(name="лаунчер")
    @commands.dm_only()
    async def launcher(self, ctx):
        characters = db.get_all_characters_normal(ctx.message.author.id)
        if characters:
            await ctx.send("Держи. Не потеряй.", file=File(fp=f"{dir_launcher}Launcher.exe",
                                                           filename=launcher_name))
        else:
            await ctx.send("Не вижу у тебя персонажей. Зачем тебе лаунчер?")

    @commands.command(aliases=['скин', 'скины'])
    @inter.exception_handler_decorator
    @check_admin_ban_decorator
    async def skins_ultimate(self, ctx, *args):

        action = None
        subject = None
        postfix = None
        attach_msg = None

        try:
            action = args[0][0]
            subject = args[0][1]
            postfix = args[0][2]
            if ctx.message.attachments[0]:
                attach_msg = ctx.message
        except (IndexError, AttributeError):
            pass

        action = await inter.skins_actions(self, ctx, plr_skin_general_tooltip, plr_skin_general_error, action)

        if action == "залить":
            character = await inter.check_char(self, ctx, plr_skin_char_tooltip, plr_skin_char_error, subject)
            postfix = await inter.input_raw_text_ascii(self, ctx, plr_skin_postfix_tooltip, forbidden_chars, postfix)
            msg = await inter.msg_with_attachment(self, ctx, plr_skin_att_tooltip, plr_skin_att_error, attach_msg)
            await util.upload_skin(ctx, character, postfix, msg)
        elif action == "получить":
            subject = await inter.input_raw_text_ascii(self, ctx, wiki_user_tooltip, forbidden_chars, subject)
            await util.get_skin_link(ctx, subject)
        elif action == "получитьвсе":
            character = await inter.check_char(self, ctx, plr_skin_get_all_tooltip, plr_skin_get_all_error, subject)
            await util.get_skins_links(ctx, character)
        elif action == "вывести":
            character = await inter.check_char(self, ctx, plr_skin_list_tooltip, plr_skin_list_error, subject)
            await util.list_skins(ctx, character)
        elif action == "уничтожить":
            subject = await inter.input_raw_text_ascii(self, ctx, plr_skin_delete_all_tooltip, forbidden_chars, subject)
            await util.skins_eraser(ctx, subject)

    @commands.command(name="персонаж")
    async def print_char_stats(self, ctx, character):
        stats_dict = mng.get({"character": character})
        await ctx.send(embed=mng_util.beautify_char_stats(stats_dict))

    @commands.command(name="параметры")
    async def print_all_parameters(self, ctx):
        await ctx.send(embed=mng_util.beautify_output_stats_names())

    @commands.command(name="статы")
    @inter.exception_handler_decorator
    @mng.exception_mongo_handler_decorator
    async def change_char_stats(self, ctx, *args):

        character = None
        ctg = None
        name = None
        mod = None

        try:
            character = args[0][0][0]
            ctg = args[0][0][1]
            name = args[0][0][2]
            mod = args[0][0][3]
        except (IndexError, AttributeError):
            pass

        character = await inter.user_or_pass(self, ctx, 15, stats_char_tooltip, gm_int_reg_char_error, character)
        ctg_rus, ctg = await inter.input_char_category(self, ctx, stats_category_tooltip, stats_category_error, ctg)
        name_rus, name = await inter.input_char_stat(self, ctx, stats_name_tooltip, stats_name_error, ctg, name)
        mod = await inter.input_number_only(self, ctx, stats_mod_tooltip, stats_mod_error, mod)

        stats = mng.get({"character": character})

        if any(x in [r.id for r in ctx.author.roles] for x in [registrar_role, admin_role]):
            if ctg_rus == "особое":
                await ctx.send(f"Теперь {name_rus} {mng.change_stat_gm(stats, ctg, name, mod)}.")
            else:
                await ctx.send(f"Теперь {ctg_rus} {name_rus} равен {mng.change_stat_gm(stats, ctg, name, mod)}.")
        else:
            if str(ctx.author.id) != stats["discord_user"]:
                await ctx.send("У тебя нет такого персонажа. Отмена.")
            else:
                await ctx.send(f"Теперь {ctg_rus} {name_rus} равен {mng.change_stat(stats, ctg, name, mod)}.")

    @commands.command(name="сгенерироватьпароль")
    async def gen_password(self, ctx, *args):
        await ctx.send(f"Сгенерированный пароль: `{pswd.generate_password()}`")

    @commands.command(name="обучение")
    @inter.exception_handler_decorator
    @mng.exception_mongo_handler_decorator
    async def learning_helper(self, ctx, *args):

        cost_of_what_needed = await inter.input_number_only(self, ctx, learning_tip_cost, learning_error)
        total_perks_already = await inter.input_number_only(self, ctx, learning_total_perks, learning_error)
        total_learned_already = await inter.input_number_only(self, ctx, learning_total_learned, learning_error)

        # сделать нормальную проверку на уровне inter функции
        if cost_of_what_needed < 0 or total_perks_already < 0 or total_learned_already < 0:
            await ctx.send("Чето тут меньше нуля. Иди в жопу.")
        else:
            current_max_learning = count_learning_cost(total_learned_already)
            needed_max_learning = count_learning_cost(total_learned_already + cost_of_what_needed)
            time_would_take = max(7, total_learned_already + total_perks_already)
            tides_or_seals = count_price(current_max_learning, needed_max_learning)

            await ctx.send(f"Итак, если ты действительно научился всему на {total_learned_already}, то твоя текущая "
                           f"фактическая обученность равна {current_max_learning}.\nТы хочешь научиться чему-то на "
                           f"{cost_of_what_needed}, а значит, тебе нужно, чтобы твоя максимальная обученность была "
                           f"{needed_max_learning}. То есть тебе нужно поднять ее на  "
                           f"{needed_max_learning - current_max_learning}.\nНа это все дело тебе нужно "
                           f"{tides_or_seals} печатей или потоков. И по времени это займет {time_would_take} "
                           f"дней, кстати.")


def setup(bot):
    bot.add_cog(PlayerCog(bot))
