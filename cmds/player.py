import glob
import os
import pathlib

from discord import User, Embed, File
from discord.ext import commands

import constants
import utility.db_handler as db

import aiohttp
import aiofiles


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='персиваль')
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
        embed.add_field(name="!лаунчер",
                        value="**Описание:** скидывает вам лаунчер в формате exe. Jar доступен у администрации. "
                              "Работает только в личке.\n**Формат:** команда\n**Пример:**  `!лаунчер`",
                        inline=False)
        embed.add_field(name="!залитьскин",
                        value="**Описание:** позволяет залить скин. Работает только в личке.\n**Формат:** команда, "
                              "затем имя персонажа, затем постфикс (не обязателен). Если постфикс есть, "
                              "имя файла будет представлять из себя \"имя персонажа + _ + постфикс\", если его нет, "
                              "то просто имя персонажа.\n**Пример:**  `!залитьскин John armor`",
                        inline=False)
        embed.add_field(name="!узнатьскины",
                        value="**Описание:** выводит имена всех ваших замечательных скинов на определенном персонаже "
                              "(включая основной и с постфиксами). Работает только в личке.\n**Формат:** команда, "
                              "затем имя персонажа.\n**Пример:**  `!узнатьскины John`",
                        inline=False)
        embed.add_field(name="!получитьскины",
                        value="**Описание:** позволяет получить все ссылки на все скины, для ленивых.\n**Формат:** "
                              "команда, затем название скина, без постфикса - только имя персонажа.\n**Пример:** "
                              "`!получитьскины John`",
                        inline=False)
        embed.add_field(name="!получитьскин",
                        value="**Описание:** позволяет получить ссылку на скин, для ленивых.\n**Формат:** команда, "
                              "затем полное имя скина (с постфиксом если есть, одним словом).\n**Пример:**  "
                              "`!получитьскин John_armor`",
                        inline=False)
        embed.add_field(name="!уничтожитьскин",
                        value="**Описание:** позволяет уничтожить скин безвозвратно.\n**Формат:** команда, "
                              "затем полное имя скина (с постфиксом если есть, одним словом).\n**Пример:**  "
                              "`!уничтожитьскин John_armor`",
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

    @commands.command(name="вики")
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
            await ctx.send("Держи. Не потеряй.", file=File(fp=f"{constants.dir_launcher}Launcher.exe",
                                                           filename=constants.launcher_name))
        else:
            await ctx.send("Не вижу у тебя персонажей. Зачем тебе лаунчер?")

    @commands.command(name="залитьскин")
    @commands.dm_only()
    async def skin_uploading(self, ctx, character, postfix=""):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            if postfix != "":
                file_name = character + "_" + postfix
            else:
                file_name = character
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url, allow_redirects=False) as r:
                    if r.headers.get('content-type') == "image/png":
                        if (int(r.headers.get('content-length')) / 1024) <= 150:  # 150 кб как можно догадаться
                            f = await aiofiles.open(f"{constants.dir_skins}/{file_name}.png", mode='wb')
                            await f.write(await r.read())
                            await f.close()
                            await ctx.send("Скин успешно залит. Отличная работа (моя). Держи:\n"
                                           f"{constants.link_skins}{file_name}.png")
                        else:
                            await ctx.send(
                                "Это слишком большой файл. Заливай через админов, я с таким дел иметь не хочу.")
                    else:
                        await ctx.send("Я не знаю что это, но это не в формате, в котором обычно кидают скины.")
        else:
            await ctx.send("У тебя нет такого персонажа. Ц-ц-ц.")

    @commands.command(name="узнатьскины")
    @commands.dm_only()
    async def list_skins(self, ctx, character):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            names = [pathlib.Path(x).stem for x in glob.glob(f"{constants.dir_skins}{character}*")]
            output = ""
            for character in names:
                if names.index(character) == (len(names) - 1):
                    output += (str(character))
                else:
                    output += (str(character) + ", ")
            await ctx.send(output)
        else:
            await ctx.send("Я не могу сказать тебе о скинах персонажей, которых у тебя нет. ")

    @commands.command(name="получитьскины")
    @commands.dm_only()
    async def get_skins_links(self, ctx, character):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        if character in available_characters:
            names = [pathlib.Path(x).stem for x in glob.glob(f"{constants.dir_skins}{character}*")]
            if names:
                output = "Держи:\n"
                for character in names:
                    if names.index(character) == (len(names) - 1):
                        output += f"{constants.link_skins}{character}.png"
                    else:
                        output += f"{constants.link_skins}{character}.png\n"
                await ctx.send(output)
            else:
                await ctx.send("Не могу ничего найти. Возможно, скинов нет?")
        else:
            await ctx.send("Я не выдаю скины персонажей, которых у тебя нет.")

    @commands.command(name="получитьскин")
    @commands.dm_only()
    async def get_skin_link(self, ctx, full_skin_name):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        for character in available_characters:
            if str(full_skin_name).startswith(character):
                if os.path.exists(f"{constants.dir_skins}{full_skin_name}.png"):
                    await ctx.send(f"Держи: {constants.link_skins}{full_skin_name}.png")
                else:
                    await ctx.send("Я не вижу такого файла. Чувствую, что где-то меня обманули.")
                return
        else:
            await ctx.send("Я не выдаю скины персонажей, которых у тебя нет. Можешь вручную сообразить, если хочешь.")

    @commands.command(name="уничтожитьскин")
    @commands.dm_only()
    async def skins_eraser(self, ctx, full_skin_name):
        available_characters = db.get_all_characters_normal(ctx.message.author.id)
        for character in available_characters:
            if str(full_skin_name).startswith(character):
                if os.path.exists(f"{constants.dir_skins}/{full_skin_name}.png"):
                    os.remove(f"{constants.dir_skins}/{full_skin_name}.png")
                    await ctx.send("Скин уничтожен. Восстановлению не подлежит. Никогда.")
                    return
                else:
                    await ctx.send("Я не вижу такого файла. Нечего уничтожать.")
                    return
        else:
            await ctx.send("Я не могу удалить скины персонажей, которых у тебя нет. Это какое-то кощунство.")


def setup(bot):
    bot.add_cog(PlayerCog(bot))
