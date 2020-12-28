import peewee

import handlers.db_handler as db
from utility.interactive_util import user_converter


async def registration(ctx, character, password, user, wiki_link):
    try:
        query = db.add_new_character(character, password, user.id, wiki_link)
    except peewee.IntegrityError:
        await ctx.send("Такой персонаж уже есть в базе данных. Отмена.")
    except db.AgeNotConfirmed:
        await ctx.send("Игрок не подтвердил возраст. Регистрация отменена. Ай-яй-яй.")
    else:
        if query == 0:
            await ctx.send("Что-то пошло не так. Свяжитесь с администрацией.")
        else:
            await ctx.send(f"Персонаж успешно зарегистрирован! Это уже {query} персонаж.")


async def delete_char(ctx, subject):
    result = db.remove_existing_character(subject)
    if result == 0:
        await ctx.send("Что-то не так. Может персонажа уже нет или ты неправильно его вбил?")
    else:
        await ctx.send("Персонаж успешно удален.")


async def delete_user(ctx, subject):
    player = await user_converter.convert(ctx, str(subject))
    result = db.remove_every_character(player.id)
    if result == 0:
        await ctx.send("Что-то не так. Может у этого игрока уже нет персонажей?")
    else:
        await ctx.send(f"**Все** персонажи <@{player.id}> успешно удалены.")


async def ban_char(ctx, subject):
    result = db.ban_character(subject)
    if result == 0:
        await ctx.send("Что-то не так. Может такого персонажа нет или он уже забанен? Так или иначе, отмена.")
    else:
        await ctx.send("Персонаж успешно забанен.")


async def ban_user(ctx, subject):
    player = await user_converter.convert(ctx, str(subject))
    result = db.ban_player(player.id)
    if result == 0:
        await ctx.send("Что-то не так. Может у этого игрока нет персонажей или уже все забанены? Так или "
                       "иначе, отмена.")
    else:
        await ctx.send(f"Персонажи <@{player.id}> успешно забанены.")


async def unban_char(ctx, subject):
    result = db.unban_character(subject)
    if result == 0:
        await ctx.send("Что-то не так. Может этот персонаж уже разбанен?")
    else:
        await ctx.send("Персонаж успешно разбанен. Так и быть, прощен.")


async def unban_user(ctx, subject):
    player = await user_converter.convert(ctx, str(subject))
    result = db.unban_player(player.id)
    if result == 0:
        await ctx.send("Что-то не так. Может, у этого игрока нет забаненных персонажей?")
    else:
        await ctx.send(f"Персонажи <@{player.id}> успешно разбанены. Амнистия!")


async def check_char(ctx, subject):
    info = db.ban_character_status(subject)
    if info is None:
        await ctx.send("У меня нет информации по этому персонажу. Возможно, его вообще нет.")
    elif info is False:
        await ctx.send("Нет, он не забанен.")
    elif info is True:
        await ctx.send("Да, он в бане. Надежно и крепко.")


async def check_user(ctx, subject):
    player = await user_converter.convert(ctx, str(subject))
    info = db.ban_player_status(player.id)
    if not info:
        await ctx.send(f"У <@{player.id}> нет забаненных персонажей, все в норме.")
    else:
        output = ""
        for character in info:
            output += (str(character))
            if info.index(character) != (len(info) - 1):
                output += (str(character) + ", ")
        await ctx.send(f"У <@{player.id}> забанены следующие персонажи: " + output)