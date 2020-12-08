from discord import User, Embed, File
from discord.ext import commands

import constants
import handlers.db_handler as db
import utility.interactive_util as inter
import utility.player_util as util
from lines import *


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['персиваль', 'команды'])
    async def help_for_players(self, ctx):
        embed = Embed()
        embed.title = "Обычные команды Персиваля"
        embed.colour = constants.color_codes["Info"]
        embed.description = "Да-да? Тут перечислены все мои команды для обычных игроков. Я, если что, не настоящий " \
                            "Персиваль, а всего-лишь бот. "
        embed.add_field(name="!персонажи",
                        value="**Описание:** выводит всех персонажей указанного игрока.\n**Формат:** команда, "
                              "затем слапнутый игрок. Можно писать его имя пользователя (не ник) или его "
                              "id.\n**Пример:** `!персонажи @John`",
                        inline=False)
        embed.add_field(name="!викиигрока",
                        value="**Описание:** дает вики-ссылки на всех персонажей игрока.\n**Формат:** команда, "
                              "затем аналогично пункту выше.\n**Пример:**  `!викиигрока @John`",
                        inline=False)
        embed.add_field(name="!википерса",
                        value="**Описание:** дает вики-ссылку на конкретного персонажа. Имя персонажа должно быть на "
                              "латиннице.\n**Формат:** команда, затем имя персонажа\n**Пример:**  `!википерса John`",
                        inline=False)
        embed.add_field(name="!пароль",
                        value="**Описание:** позволяет сменить пароль. Работает только в личке.\n**Формат:** команда, "
                              "затем имя персонажа, затем новый пароль.\n**Пример:**  `!пароль John q1w2e3`",
                        inline=False)
        embed.add_field(name="!лаунчер",
                        value="**Описание:** скидывает вам лаунчер в формате exe. Jar доступен у администрации. "
                              "Работает только в личке.\n**Формат:** команда\n**Пример:**  `!лаунчер`",
                        inline=False)
        embed.add_field(name="!скин или !скины",
                        value="**Описание:** интерактивная команда. Работает только в личке. Весь массив операций со "
                              "скинами, будь это их удаление, добавление и пр.\n**Формат:** "
                              'подсказывается по ходу, но можно забивать аргументы "наперед". Сначала указывается '
                              'действие (залить, получить ссылку, вывести все, получить все ссылки, уничтожить) затем '
                              'строго контекстуально. Если это заливание, то нужно указать имя персонажа, затем '
                              'постфикс, ("Нет" считается отсутствием постфикса), затем нужно приложить пост с файлом. '
                              'Как уже было сказано, можно миксовать как угодно, например заранее написать '
                              '**!скин залить Vasya armor** а следующим сообщением залить файл. А можно сразу все. А  '
                              'можно просто **!скин залить Vasya**, а потом указать постфикс и отправить сообщение '
                              'со скином.\n**Пример:** `!скин`',
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="персонажи")
    async def characters(self, ctx, user: User = None):
        if not user:
            user = ctx.message.author
        list_of_characters = db.get_all_characters_normal(user.id)
        output = ""
        for character in list_of_characters:
            if list_of_characters.index(character) == (len(list_of_characters) - 1):
                output += (str(character))
            else:
                output += (str(character) + ", ")
        await ctx.send(output)

    @commands.command(name="википерса")
    async def wiki_char(self, ctx, character):
        output = db.get_character_link(character)
        await ctx.send(output)

    @commands.command(name="викиигрока")
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
    # @commands.dm_only()
    async def password_change(self, ctx, character, password):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            db.set_new_password(character, password)
            await ctx.send("Новый пароль задан.")
        else:
            await ctx.send("У тебя нет такого персонажа. Что-то тут не так.")

    @commands.command(name="лаунчер")
    # @commands.dm_only()
    async def launcher(self, ctx):
        characters = db.get_all_characters_normal(ctx.message.author.id)
        if characters:
            await ctx.send("Держи. Не потеряй.", file=File(fp=f"{constants.dir_launcher}Launcher.exe",
                                                           filename=constants.launcher_name))
        else:
            await ctx.send("Не вижу у тебя персонажей. Зачем тебе лаунчер?")

    @commands.command(aliases=['скин', 'скины'])
    @inter.exception_handler_decorator
    # @commands.dm_only()
    async def skins_ultimate(self, ctx, *args):

        action = None
        subject = None
        postfix = None
        attachment = None

        try:
            action = args[0][0]
            subject = args[0][1]
            postfix = args[0][2]
            attachment = ctx.message.attachments[0]
        except IndexError:
            pass
        except AttributeError:
            pass

        if not action:
            action = await inter.skins_actions(self, ctx, plr_skin_general_tooltip, plr_skin_general_error)

        if action == "залить":
            character = await inter.check_char(self, ctx, plr_skin_char_tooltip, plr_skin_char_error, subject)
            if not postfix:
                postfix = await inter.input_raw_text(self, ctx, plr_skin_postfix_tooltip)
            if not attachment:
                msg = await inter.msg_with_attachment(self, ctx, plr_skin_att_tooltip, plr_skin_att_error)
            else:
                msg = ctx.message
            await util.upload_skin(ctx, character, postfix, msg)
        elif action == "получить":
            if not subject:
                subject = await inter.input_raw_text(self, ctx, plr_skin_link_or_del_tooltip)
            await util.get_skin_link(ctx, subject)
        elif action == "получитьвсе":
            character = await inter.check_char(self, ctx, plr_skin_get_all_tooltip, plr_skin_get_all_error, subject)
            await util.get_skins_links(ctx, character)
        elif action == "вывести":
            character = await inter.check_char(self, ctx, plr_skin_list_tooltip, plr_skin_list_error, subject)
            await util.list_skins(ctx, character)
        elif action == "уничтожить":
            if not subject:
                subject = await inter.input_raw_text(self, ctx, plr_skin_link_or_del_tooltip)
            await util.skins_eraser(ctx, subject)


def setup(bot):
    bot.add_cog(PlayerCog(bot))
