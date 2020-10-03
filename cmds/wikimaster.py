from discord import Embed
from discord.ext import commands

import constants
import utility.mediawiki_handler as mw


class WikiMasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='викимастерская')
    @commands.has_role(constants.wiki_registrar_role)
    @commands.guild_only()
    async def help_for_moderation(self, ctx):
        embed = Embed()
        embed.title = "Команды для вики-мастеров"
        embed.colour = constants.color_codes["Info"]
        embed.title = ""
        embed.description = " "
        embed.add_field(name="!вики-регистрация",
                        value="**Описание:** регистрирует нового пользователя на вики.\n**Формат:** команда, "
                              "имя нового аккаунта, пароль.\n**Пример:**  `Вики-регистрация John qwerty`",
                        inline=False)
        embed.add_field(name="!вики-бан",
                        value="**Описание:** банит пользователя на вики. Все баны через эту команду "
                              "бессрочные.\n**Формат:** команда, имя аккаунта для бана, причина. \n**Пример:**  "
                              "`Вики-бан John вандализм`",
                        inline=False)
        embed.add_field(name="!вики-разбан",
                        value="**Описание:** разбанивает пользователя на вики.\n**Формат:** команда, имя аккаунта для "
                              "разбана, причина.\n**Пример:**  `Вики-разбан John извинился`",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="вики-регистрация")
    @commands.has_role(constants.wiki_registrar_role)
    @commands.guild_only()
    async def wiki_register(self, ctx, username, password):
        result = mw.create_wiki_account(username, password)
        if result is True:
            await ctx.send("Аккаунт на вики успешно создан.")
        else:
            await ctx.send(
                "Аккаунт на вики создать не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")

    @commands.command(name="вики-бан")
    @commands.has_role(constants.wiki_registrar_role)
    @commands.guild_only()
    async def wiki_ban(self, ctx, username, reason):
        result = mw.ban_wiki_account(username, reason)
        if result is True:
            await ctx.send("Аккаунт на вики успешно забанен.")
        else:
            await ctx.send(
                "Аккаунт на вики забанить не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")

    @commands.command(name="вики-разбан")
    @commands.has_role(constants.wiki_registrar_role)
    @commands.guild_only()
    async def wiki_unban(self, ctx, username, reason):
        result = mw.unban_wiki_account(username, reason)
        if result is True:
            await ctx.send("Аккаунт на вики успешно разбанен.")
        else:
            await ctx.send(
                "Аккаунт на вики разбанить не получилось. Сообщение от нашей милой MediaWiki:\n" + "```" + result + "```")


def setup(bot):
    bot.add_cog(WikiMasterCog(bot))
