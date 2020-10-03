from discord import Embed
from discord.ext import commands

import constants


class DiscordErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def print_error_in_embed(self, ctx, is_error=False, body='ERROR!'):
        debug_channel = self.bot.get_channel(constants.log_channel)
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
        print(error)  # beware, это логирует все ошибки в консоль
        if isinstance(error, commands.errors.PrivateMessageOnly):
            await ctx.send("Это не личные сообщения. ТАКОЕ я готов обсуждать только там.")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Недостаточно аргументов. Проверь правильность команды.")
        elif isinstance(error, commands.errors.UserNotFound):
            await ctx.send("Я не могу найти этого пользователя. Ты точно все правильно вбил?")
        elif isinstance(error, commands.errors.MissingRole):
            required_role_id = int(str(error).split()[1])
            if required_role_id == constants.registrar_role:
                await ctx.send('Ты даже не регистратор! Крайне дерзко с твоей стороны.')
            elif required_role_id == constants.wiki_registrar_role:
                await ctx.send('Ты не вики-мастер. Меня так просто не проведешь.')
        elif isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.send('Я таким не занимаюсь в личных сообщениях. Только на сервере.')
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send('Воу-воу. Полегче. Эта команда пока на кулдауне.')


def setup(bot):
    bot.add_cog(DiscordErrorHandler(bot))
