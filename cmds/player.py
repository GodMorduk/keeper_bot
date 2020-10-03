import glob
import os
import pathlib

import requests
from discord import User, Embed
from discord.ext import commands

import constants
import utility.db_handler as db


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='персиваль')
    @commands.guild_only()
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
                              "затем аналогично пункту выше.\n**Пример:**  `!вики @John`",
                        inline=False)
        embed.add_field(name="!вики",
                        value="**Описание:** дает вики-ссылку на конкретного персонажа. Имя персонажа должно быть на "
                              "латиннице.\n**Формат:** команда, затем имя персонажа\n**Пример:**  `!вики John`",
                        inline=False)
        embed.add_field(name="!пароль",
                        value="**Описание:** позволяет сменить пароль. Работает только в личке.\n**Формат:** команда, "
                              "затем имя персонажа, затем новый пароль.\n**Пример:**  `!пароль John q1w2e3`",
                        inline=False)
        embed.add_field(name="!залить",
                        value="**Описание:** позволяет залить скин. Работает только в личке.\n**Формат:** команда, "
                              "затем имя персонажа, затем постфикс (не обязателен). Если постфикс есть, "
                              "имя файла будет представлять из себя \"имя персонажа + _ + постфикс\", если его нет, "
                              "то просто имя персонажа.\n**Пример:**  `!залить John armor`",
                        inline=False)
        embed.add_field(name="!вывести",
                        value="**Описание:** выводит имена всех ваших замечательных скинов на определенном персонаже "
                              "(включая основной и с постфиксами). Работает только в личке.\n**Формат:** команда, "
                              "затем имя персонажа.\n**Пример:**  `!узнать John`",
                        inline=False)
        embed.add_field(name="!получить",
                        value="**Описание:** позволяет получить ссылку на скин, для ленивых.\n**Формат:** команда, "
                              "затем полное имя скина (с постфиксом если есть, одним словом).\n**Пример:**  "
                              "`!получить John_armor`",
                        inline=False)
        embed.add_field(name="!уничтожить",
                        value="**Описание:** позволяет уничтожить скин безвозвратно.\n**Формат:** команда, "
                              "затем полное имя скина (с постфиксом если есть, одним словом).\n**Пример:**  "
                              "`!уничтожить John_armor`",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="персонажи")
    @commands.guild_only()
    async def characters(self, ctx, user: User):
        list_of_characters = db.get_all_characters_normal(user.id)
        output = ""
        for character in list_of_characters:
            if list_of_characters.index(character) == (len(list_of_characters)-1):
                output += (str(character))
            else:
                output += (str(character) + ", ")
        await ctx.send(output)

    @commands.command(name="вики")
    @commands.guild_only()
    async def wiki_char(self, ctx, character):
        output = db.get_character_link(character)
        await ctx.send(output)

    @commands.command(name="викиигрока")
    @commands.guild_only()
    @commands.cooldown(1, 15.0, commands.BucketType.default)
    async def wiki_players(self, ctx, user: User):
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
            await ctx.send("Не ври мне, у тебя нет такого персонажа!")

    @commands.command(name="залить")
    # @commands.dm_only()
    async def skins_creation(self, ctx, character, postfix=""):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            if postfix != "":
                file_name = character + "_" + postfix
            else:
                file_name = character
            r = requests.get(ctx.message.attachments[0].url, allow_redirects=False)
            if r.headers.get('content-type') == "image/png":
                if (int(r.headers.get('content-length', None)) / 1024) <= 150:  # 150 кб как можно догадаться
                    open(f"{constants.dir_skins}/{file_name}.png", 'wb').write(r.content)
                    await ctx.send("Скин успешно залит. Отличная работа (моя). Держи:\n "
                                   f"{constants.link_skins}{file_name}.png")
                else:
                    await ctx.send("Это слишком большой файл. Заливай через админов, я с таким дел иметь не хочу.")
            else:
                await ctx.send("Я не знаю что это, но это не в формате, в котором обычно кидают скины.")
        else:
            await ctx.send("У тебя нет такого персонажа. Ц-ц-ц.")

    @commands.command(name="вывести")
    # @commands.dm_only()
    async def skins_lists(self, ctx, character):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            names = [pathlib.Path(x).stem for x in glob.glob(f"{constants.dir_skins}/{character}*")]
            output = ""
            for character in names:
                if names.index(character) == (len(names) - 1):
                    output += (str(character))
                else:
                    output += (str(character) + ", ")
            await ctx.send(output)
        else:
            await ctx.send("Я не могу сказать тебе о скинах персонажей, которых у тебя нет. ")

    @commands.command(name="получить")
    # @commands.dm_only()
    async def skins_get_link(self, ctx, full_skin_name):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        for character in available_characters:
            if str(full_skin_name).startswith(character):
                if os.path.exists(f"{constants.dir_skins}/{full_skin_name}.png"):
                    await ctx.send(f"Держи: {constants.link_skins}{full_skin_name}.png")
                else:
                    await ctx.send("Я не вижу такого файла. Чувствую, что где-то меня обманули.")
                return
        else:
            await ctx.send("Я не выдаю скины персонажей, которых у тебя нет. Можешь вручную сообразить, если хочешь.")

    @commands.command(name="уничтожить")
    # @commands.dm_only()
    async def skins_eraser(self, ctx, full_skin_name):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        for character in available_characters:
            if str(full_skin_name).startswith(character):
                if os.path.exists(f"{constants.dir_skins}/{full_skin_name}.png"):
                    os.remove(f"{constants.dir_skins}/{full_skin_name}.png")
                    await ctx.send("Скин уничтожен. Восстановлению не подлежит. Никогда.")
                else:
                    await ctx.send("Я не вижу такого файла. Нечего уничтожать.")
                return
        else:
            await ctx.send("Я не могу удалить скины персонажей, которых у тебя нет. Это какое-то кощунство.")


def setup(bot):
    bot.add_cog(PlayerCog(bot))
