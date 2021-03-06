import asyncio
import re

from discord.ext import commands

import handlers.mysql_handler as db
from config_values import timeout, prefix, wiki_url
from utility.discord_util import user_converter
from utility.mongo_util import dict_category, dict_skills, dict_attrs, dict_efforts, dict_tides, dict_special
from lines import plr_rule_confirmation_tip, plr_age_confirmation_tip, plr_age_confirmation_error

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
                if re.match(f"^{prefix}.*|^<@!?{self.bot.user.id}>.*", m.content):
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
            await ctx.send("Я вижу попытку ввести команду, когда ты уже в интерактивной команде. Не делай так, ладно?")
            return
        except asyncio.TimeoutError:
            await ctx.send("Ты слишком долго не отвечаешь. Отмена операции.")
            return
        except MaxNumberOfTriesReached:
            await ctx.send("Слишком много неудачных попыток. Команда отменена.")
        except db.PlayerBannedForever:
            await ctx.send("Этот игрок в черном списке администрации. Я не буду выполнять с ним никаких операций.")
        else:
            return func_execution

    return exception_handler_wrapper


async def get_subject_if_none(self, check, return_message_itself=False):
    message = await self.bot.wait_for('message', timeout=timeout, check=check)
    subject = str(message.content)

    if subject.lower() == "отмена":
        raise CommandIsCancelled()

    if return_message_itself:
        return message
    else:
        return subject


# Сами модули

@do_check_decorator
async def user_or_pass(check, self, ctx, len_max, tip_text, error_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if len(subject) > len_max or subject.isascii() is False:
            await ctx.send(error_text)
            subject = None
            continue
        return subject


@do_check_decorator
async def discord_user_get_id(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if len(subject) == 18 and subject.isdecimal():
            pass
        else:
            try:
                subject = await user_converter.convert(ctx, subject)
                subject = subject.id
            except commands.errors.MemberNotFound:
                await ctx.send(error_text)
                subject = None
                continue
        if db.check_player_ban_by_id(subject):
            raise db.PlayerBannedForever
        else:
            return subject


@do_check_decorator
async def one_or_another(check, self, ctx, tip_text, error_text, subject=None,
                         first_name="персонажа", second_name="игрока"):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if subject != first_name and subject != second_name:
            await ctx.send(error_text)
            subject = None
            continue
        return subject


@do_check_decorator
async def skins_actions(check, self, ctx, tip_text, error_text, subject=None):
    possible_commands = ["залить", "получить", "вывести", "получитьвсе", "уничтожить"]
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if subject not in possible_commands:
            await ctx.send(error_text)
            subject = None
            continue
        return subject


@do_check_decorator
async def check_char(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if db.is_such_char(subject) is False:
            await ctx.send(error_text)
            subject = None
            continue
        return subject


@do_check_decorator
async def msg_with_attachment(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check, return_message_itself=True)
        if not subject.attachments:
            await ctx.send(error_text)
            subject = None
            continue
        return subject


@do_check_decorator
async def input_raw_text_ascii(check, self, ctx, tip_text, error_text=None, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if subject.isascii() is False:
            await ctx.send(error_text)
            subject = None
            continue
        return subject


@do_check_decorator
async def input_raw_text_no_checks(check, self, ctx, tip_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        return subject


@do_check_decorator
async def input_wiki_link(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        if not subject.startswith(wiki_url):
            await ctx.send(error_text)
            subject = None
            continue
        return subject


# Особое, поскольку без первого раза и с ошибками

@do_check_decorator
async def age_confirmation(check, self, ctx):
    mistakes = 0
    while True:
        if mistakes == 3:
            await ctx.send("Ты три раза написал неправильно. Думаю, на сегодня с тебя хватит. Отменяю.")
            raise MaxNumberOfTriesReached()
        if mistakes > 0:
            await ctx.send(plr_age_confirmation_error)

        await ctx.send(plr_age_confirmation_tip)
        result = await self.bot.wait_for('message', timeout=3600, check=check)
        if result.content.lower() == "отмена":
            raise CommandIsCancelled()
        elif result.content.lower().strip(".") == "подтверждаю, что мне исполнилось 18 лет и я совершеннолетний":
            await ctx.send(plr_rule_confirmation_tip)
            result = await self.bot.wait_for('message', timeout=3600, check=check)
            if result.content.lower() == "отмена":
                raise CommandIsCancelled()
            elif result.content.lower().strip(".") == "я ознакомился с правилами проекта, с ними полностью согласен " \
                                                      "и обязуюсь их соблюдать, а так же безоговорочно признаю за " \
                                                      "администрацией проекта право на их интерпретацию":
                return True
            else:
                mistakes += 1
                continue
        else:
            mistakes += 1
            continue


# Персонажное

@do_check_decorator
async def input_char_category(check, self, ctx, tip_text, error_text, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        subject = subject.lower()
        try:
            subject_eng = dict_category[subject]
            return subject, subject_eng
        except KeyError:
            await ctx.send(error_text)
            subject = None
            continue


@do_check_decorator
async def input_char_stat(check, self, ctx, tip_text, error_text, category, subject=None):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        subject = subject.lower()
        try:
            if category == "skills":
                subject_eng = dict_skills[subject]
                return subject, subject_eng
            elif category == "attributes":
                subject_eng = dict_attrs[subject]
                return subject, subject_eng
            elif category == "efforts":
                subject_eng = dict_efforts[subject]
                return subject, subject_eng
            elif category == "tides":
                subject_eng = dict_tides[subject]
                return subject, subject_eng
            elif category == "special_stats":
                subject_eng = dict_special[subject]
                return subject, subject_eng
        except KeyError:
            await ctx.send(error_text)
            subject = None
            continue


@do_check_decorator
async def input_number_only(check, self, ctx, tip_text, error_text, subject=None, return_as_int=False):
    if not subject:
        await ctx.send(tip_text)
    while True:
        if not subject:
            subject = await get_subject_if_none(self, check)
        try:
            int_subject = int(subject)
            if return_as_int:
                return int_subject
            else:
                return subject

        except ValueError:
            await ctx.send(error_text)
            subject = None
            continue
