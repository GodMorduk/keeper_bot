from discord import User, Embed, File
from discord.ext import commands

from config_values import prefix, dir_launcher, launcher_name, bot_name, bot_genitive_name
import constants
import handlers.db_handler as db
import utility.interactive_util as inter
import utility.player_util as util
from utility.discord_util import user_converter
from lines import *
from cmds.admin import check_admin_ban_decorator


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
        await ctx.send(embed=embed)

    @commands.command(name="подтвердитьвозраст")
    @commands.guild_only()
    @commands.cooldown(1, 86400.0, commands.BucketType.user)
    @inter.exception_handler_decorator
    @check_admin_ban_decorator
    async def age_confirmation(self, ctx, *args):

        try:
            current_state = db.get_if_age_confirmed(ctx.message.author.id)
        except db.AgeNotConfirmed:
            current_state = False

        if current_state:
            await ctx.send(plr_age_confirmation_already)
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(plr_age_confirmation_tip)
            result = await inter.age_confirmation(self, ctx, plr_age_confirmation_error)
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
            postfix = await inter.input_raw_text_no_checks(self, ctx, plr_skin_postfix_tooltip, postfix)
            msg = await inter.msg_with_attachment(self, ctx, plr_skin_att_tooltip, plr_skin_att_error, attach_msg)
            await util.upload_skin(ctx, character, postfix, msg)

        elif action == "получить":
            subject = await inter.input_raw_text_ascii_only(self, ctx, wiki_user_tooltip, forbidden_chars, subject)
            await util.get_skin_link(ctx, subject)
        elif action == "получитьвсе":
            character = await inter.check_char(self, ctx, plr_skin_get_all_tooltip, plr_skin_get_all_error, subject)
            await util.get_skins_links(ctx, character)
        elif action == "вывести":
            character = await inter.check_char(self, ctx, plr_skin_list_tooltip, plr_skin_list_error, subject)
            await util.list_skins(ctx, character)
        elif action == "уничтожить":
            subject = await inter.input_raw_text_ascii_only(self, ctx, plr_skin_delete_all_tooltip, forbidden_chars, subject)
            await util.skins_eraser(ctx, subject)


def setup(bot):
    bot.add_cog(PlayerCog(bot))
