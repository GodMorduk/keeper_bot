import glob
import os
import pathlib

import aiofiles
import aiohttp

import constants
import handlers.db_handler as db


async def upload_skin(ctx, character, postfix, skin_message=None):
    if postfix == "Нет" or postfix == "":
        file_name = character
    else:
        file_name = character + "_" + postfix
    async with aiohttp.ClientSession() as session:

        if skin_message is None:
            m = ctx.message
        else:
            m = skin_message
        async with session.get(m.attachments[0].url, allow_redirects=False) as r:
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


async def get_skin_link(ctx, full_skin_name):
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


async def get_skins_links(ctx, character):
    available_characters = db.get_all_characters_normal(ctx.message.author.id)
    if character in available_characters:
        names = [pathlib.Path(x).stem for x in glob.glob(f"{constants.dir_skins}{character}*")]
        if names:
            output = "Держи:\n"
            for character in names:
                output += f"{constants.link_skins}{character}.png"
                if names.index(character) != (len(names) - 1):
                    output += "\n"
            await ctx.send(output)
        else:
            await ctx.send("Не могу ничего найти. Возможно, скинов нет?")
    else:
        await ctx.send("Я не выдаю скины персонажей, которых у тебя нет.")


async def list_skins(ctx, character):
    available_characters = db.get_all_characters_normal(ctx.message.author.id)
    if character in available_characters:
        names = [pathlib.Path(x).stem for x in glob.glob(f"{constants.dir_skins}{character}*")]
        output = ""
        for character in names:
            if names.index(character) == (len(names) - 1):
                output += "`"
                output += (str(character)) + "`"
            else:
                output += "`"
                output += (str(character) + "`, ")
        await ctx.send(output)
    else:
        await ctx.send("Я не могу сказать тебе о скинах персонажей, которых у тебя нет. ")


async def skins_eraser(ctx, full_skin_name):
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
