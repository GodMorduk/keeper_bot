import asyncio
import re

from discord.ext import commands

import handlers.db_handler as db
from utility.discord_util import user_converter


class CommandIsCancelled(commands.CommandError):
    pass


class UserAlreadyInInteractiveCommand(commands.CommandError):
    pass


class MaxNumberOfTriesReached(commands.CommandError):
    pass


def do_check_decorator(func):
    def do_check_wrapper(self, ctx, *args, **kwargs):
        def check(m):
            if m.author == ctx.author and m.channel == ctx.channel:
                if re.match(f"^!.*|^<@!?{self.bot.user.id}>.*", m.content):
                    raise UserAlreadyInInteractiveCommand
                else:
                    return True

        func_execution = func(check, self, ctx, *args, **kwargs)
        return func_execution

    return do_check_wrapper


def exception_handler_decorator(func):
    async def exception_handler_wrapper(self, ctx, *args, **kwargs):
        try:
            func_execution = await func(self, ctx, args, kwargs)
        except CommandIsCancelled:
            await ctx.send("Ты отменил команду. Она, внезапно, отменена.")
            return
        except UserAlreadyInInteractiveCommand:
            await ctx.send("Я вижу попытку ввести команду, когда ты уже в интерактивной команде. Отменяю предыдущую. "
                           "Не делай так, ладно?")
            return
        except asyncio.TimeoutError:
            await ctx.send("Ты слишком долго не отвечаешь. Отмена операции.")
            return
        except MaxNumberOfTriesReached:
            await ctx.send("Слишком много неудачных попыток. Команда отменена.")
        else:
            return func_execution

    return exception_handler_wrapper


# Сами модули

@do_check_decorator
async def max_len(check, self, ctx, len_max, tip_text, error_text, subject=None):
    if not subject:
        first_time = True
    else:
        first_time = False
    while True:
        await asyncio.sleep(1)
        if first_time:
            await ctx.send(tip_text)
        if not subject:
            result = await self.bot.wait_for('message', timeout=30.0, check=check)
            result = str(result.content)
        else:
            result = subject
        if result.lower() == "отмена":
            raise CommandIsCancelled()
        else:
            if len(result) > len_max:
                await ctx.send(error_text)
                first_time = False
                subject = None
                continue
            return result


@do_check_decorator
async def discord_user(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        first_time = True
    else:
        first_time = False
    while True:
        await asyncio.sleep(1)
        if first_time:
            await ctx.send(tip_text)
        if not subject:
            result = await self.bot.wait_for('message', timeout=30.0, check=check)
            result = str(result.content)
        else:
            result = subject
        if result.lower() == "отмена":
            raise CommandIsCancelled()
        else:
            try:
                result = await user_converter.convert(ctx, result)
            except commands.errors.MemberNotFound:
                await ctx.send(error_text)
                first_time = False
                continue
        return result


@do_check_decorator
async def user_or_char(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        first_time = True
    else:
        first_time = False
    while True:
        await asyncio.sleep(1)
        if first_time:
            await ctx.send(tip_text)
        if not subject:
            result = await self.bot.wait_for('message', timeout=30.0, check=check)
            result = str(result.content)
        else:
            result = subject
        if result.lower() == "отмена":
            raise CommandIsCancelled()
        if result != "персонажа" and result != "игрока":
            await ctx.send(error_text)
            first_time = False
            continue
        else:
            return result


@do_check_decorator
async def skins_actions(check, self, ctx, tip_text, error_text):
    possible_commands = ["залить", "получить", "вывести", "получитьвсе", "уничтожить"]
    first_time = True
    while True:
        await asyncio.sleep(1)
        if first_time:
            await ctx.send(tip_text)
        result = await self.bot.wait_for('message', timeout=30.0, check=check)
        result = str(result.content)
        if result.lower() == "отмена":
            raise CommandIsCancelled()
        if result not in possible_commands:
            await ctx.send(error_text)
            first_time = False
            continue
        else:
            return result


@do_check_decorator
async def check_char(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        first_time = True
    else:
        first_time = False

    while True:
        await asyncio.sleep(1)
        if first_time:
            await ctx.send(tip_text)

        if not subject:
            result = await self.bot.wait_for('message', timeout=30.0, check=check)
            result = str(result.content)
        else:
            result = subject

        if result.lower() == "отмена":
            raise CommandIsCancelled()

        if db.is_such_char(result) is False:
            await ctx.send(error_text)
            first_time = False
            subject = None
            continue
        else:
            return result


@do_check_decorator
async def input_raw_text(check, self, ctx, tip_text):
    await ctx.send(tip_text)
    result = await self.bot.wait_for('message', timeout=30.0, check=check)
    result = str(result.content)
    if result.lower() == "отмена":
        raise CommandIsCancelled()
    else:
        return result


@do_check_decorator
async def msg_with_attachment(check, self, ctx, tip_text, error_text):
    first_time = True
    while True:
        if first_time:
            await ctx.send(tip_text)
        result = await self.bot.wait_for('message', timeout=30.0, check=check)
        if result.content.lower() == "отмена":
            raise CommandIsCancelled()
        elif not result.attachments:
            await ctx.send(error_text)
            first_time = False
            continue
        else:
            return result


@do_check_decorator
async def msg_with_attachment(check, self, ctx, tip_text, error_text):
    first_time = True
    while True:
        if first_time:
            await ctx.send(tip_text)
        result = await self.bot.wait_for('message', timeout=30.0, check=check)
        if result.content.lower() == "отмена":
            raise CommandIsCancelled()
        elif not result.attachments:
            await ctx.send(error_text)
            first_time = False
            continue
        else:
            return result


@do_check_decorator
async def age_confirmation(check, self, ctx, error_text):
    mistakes = 0
    while True:
        if mistakes == 3:
            await ctx.send("Ты три раза написал неправильно. Думаю, на сегодня с тебя хватит. Отменяю.")
            raise MaxNumberOfTriesReached()
        if mistakes > 0:
            await ctx.send(error_text)
        result = await self.bot.wait_for('message', timeout=30.0, check=check)
        if result.content.lower() == "отмена":
            raise CommandIsCancelled()
        elif result.content.lower().strip(".") == "подтверждаю, что мне исполнилось 18 лет и я совершеннолетний":
            return True
        else:
            mistakes += 1
            continue
