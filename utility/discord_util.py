import asyncio
import re

from discord import Embed
from discord.ext import commands

import config_values
import constants

user_converter = commands.MemberConverter()
role_converter = commands.RoleConverter()


class DiscordUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def print_error_in_embed(self, ctx, is_error=False, body='ERROR!'):
        debug_channel = self.bot.get_channel(config_values.log_channel)
        embed = Embed()
        embed.add_field(name="Кто", value=ctx.author)
        embed.add_field(name="Команда:", value=ctx.message.content)
        channel_as_string = str(ctx.message.channel)
        if channel_as_string.startswith("Direct Message"):
            get_username = "Личные сообщения"
        else:
            get_username = f"<#{ctx.message.channel.id}>"
        embed.add_field(name="Где:", value=get_username)
        if is_error:
            embed.title = "Ошибка!"
            embed.colour = constants.color_codes["Error"]
            embed.add_field(name="Ошибка", value=body)
        else:
            embed.title = "Обычные логи"
            embed.colour = constants.color_codes["Log"]
        await debug_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        else:
            print("Caught error! " + str(error))
            if config_values.log_enable:
                await self.print_error_in_embed(ctx, is_error=True, body=error)
            if str(error).endswith("Cannot send an empty message"):  # потому что там ошибка bad request
                await ctx.send("Не могу ничего отправить. Сообщение пустое по какой-то причине.")
            elif "Please choose a more unique password" in str(error):
                await ctx.send("Этот пароль слишком не-уникальный.")
            elif "No such user" in str(error):
                await ctx.send("Такого пользователя не существует. Вообще.")
            elif isinstance(error, commands.errors.PrivateMessageOnly):
                await ctx.send("Это не личные сообщения. ТАКОЕ я готов обсуждать только там.")
            elif isinstance(error, commands.errors.MissingRequiredArgument):
                await ctx.send("Недостаточно аргументов. Проверь правильность команды.")
            elif isinstance(error, commands.errors.UserNotFound):
                await ctx.send("Я не могу найти этого пользователя. Ты точно все правильно вбил?")
            elif isinstance(error, commands.errors.MissingAnyRole):
                required_role_id = int(str(error.missing_roles[0]))
                if required_role_id == config_values.registrar_role:
                    await ctx.send('Ты даже не регистратор! Крайне дерзко с твоей стороны.')
                elif required_role_id == config_values.wiki_registrar_role:
                    await ctx.send('Ты не вики-мастер. Меня так просто не проведешь.')
            elif isinstance(error, commands.errors.MissingRole):
                required_role_id = int(str(error.missing_role))
                if required_role_id == config_values.admin_role:
                    await ctx.send('Ты не админ! Тебе нельзя такие штуки!')
            elif isinstance(error, commands.errors.NoPrivateMessage):
                await ctx.send('Я таким не занимаюсь в личных сообщениях. Только на сервере.')
            elif isinstance(error, commands.errors.CommandOnCooldown):
                if "подтвердитьвозраст" in str(ctx.message.content):
                    await ctx.send("Ты сегодня уже неудачно подтверждал возраст. Попробуй завтра, может завтра "
                                   "повзрослеешь.")
                else:
                    msg = await ctx.send(f'Воу-воу. Полегче. Эта команда пока на кулдауне. Подожди еще '
                                         f'{round(error.retry_after)} секунд.')
                    await asyncio.sleep(config_values.timeout)
                    await ctx.message.delete()
                    await msg.delete()

    @commands.Cog.listener("on_message")
    async def show_help(self, msg):
        ctx = await self.bot.get_context(msg)
        if re.match(f"^<@!?{self.bot.user.id}>.*", msg.content) and not ctx.valid:
            await ctx.send(f"Привет. Я бот {config_values.bot_name}. Мои команды можно посмотреть, если сказать мне "
                           f"'{config_values.bot_name}' или 'команды'.\nМои префиксы (что писать перед командой, чтобы "
                           f"я обратил на тебя внимание): это \"{config_values.prefix}\" или можно меня слапнуть, "
                           f"сопроводив это командой. В случае слапа нужен пробел.\n**Примеры команд:** "
                           f"`{config_values.prefix}{config_values.bot_name} или `@{config_values.bot_name} команды`.")


def setup(bot):
    bot.add_cog(DiscordUtil(bot))
