from discord import User, Embed
from discord.ext import commands

import constants
import utility.db_handler as db
from constants import registrar_role


class GameMasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='гейммастерская')
    @commands.has_role(registrar_role)
    @commands.guild_only()
    async def help_for_moderation(self, ctx):
        embed = Embed()
        embed.title = "Команды для гейм-мастеров и регистраторов:"
        embed.colour = constants.color_codes["Info"]
        embed.description = "Вводите с осторожностью, перепроверяйте команды и все такое. Непоправимого мало, " \
                            "а вот неприятного и так достаточно. "
        embed.add_field(name="!зарегистрировать",
                        value="**Описание:** регистрирует нового персонажа. \n**Формат:** команда, имя персонажа ("
                              "латинница с большой буквы), пароль, затем слап или id или юзернейм (не ник) игрока, "
                              "и наконец прямая ссылка на вики \n**Пример:** `!зарегистрировать John qwerty @John "
                              "https://google.com`",
                        inline=False)
        embed.add_field(name="!удалить",
                        value='**Описание:** удаляет персонажа либо игрока. Навсегда.\n**Формат:** команда, '
                              'слово "персонажа" или "игрока", затем соотв-но имя персонажа или имя (можно передать '
                              'через юзернейм (не ник), слап, id) игрока.\n**Пример:**  `!удалить игрока @John`\n',
                        inline=False)
        embed.add_field(name="!дамп",
                        value="**Описание:** Выводит всю инфу обо всех персонажах игрока. Доступ только по "
                              "id.\n**Формат:** команда, id игрока. \n**Пример:**  `!дамп 123412341234123412`\n",
                        inline=False)
        embed.add_field(name="!забанить",
                        value='**Описание:** банит (но не удаляет) игрока в базе данных (не в игре и не в '
                              'дискорде).\n**Формат:** аналогичный с командой "удалить".\n**Пример:**  `!забанить '
                              'персонажа John`\n',
                        inline=False)
        embed.add_field(name="!разбанить",
                        value='**Описание:** разбанивает одного персонажа или всех персонажей игрока.\n**Формат:** '
                              'аналогичный с командой "удалить"\n**Пример:**  `!разбанить игрока John"`\n',
                        inline=False)
        embed.add_field(name="!проверить",
                        value="**Описание:** если спрашивают об игроке, выводит всех его забаненных персонажей, "
                              "если о персонаже - пишет, забанен ли он.\n**Формат:** аналогичный с командой "
                              "'удалить'\n**Пример:**  `!проверить игрока John `\n",
                        inline=False)
        embed.add_field(name="!судо-пароль",
                        value="**Описание:** меняет пароль на персонаже, даже если вы не его владелец.\n**Формат:** "
                              "команда, затем имя персонажа, затем новый пароль.\n**Пример:**  `!судо-пароль John "
                              "qwerty123`\n",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="зарегистрировать")
    @commands.has_role(registrar_role)
    @commands.guild_only()
    async def register(self, ctx, character, password, user: User, wiki_link):
        db.add_new_player(character, password, user.id, wiki_link)
        await ctx.send("Персонаж успешно зарегистрирован!")

    @commands.command(name="удалить")
    @commands.guild_only()
    @commands.has_role(registrar_role)
    async def delete(self, ctx, type, subject):
        if type == "персонажа":
            db.remove_existing_character(subject)
            await ctx.send("Персонаж успешно удален.")
        elif type == "игрока":
            try:
                player = await commands.UserConverter().convert(ctx, str(subject))
                db.remove_every_character(player.id)
            except commands.UserNotFound:
                db.remove_every_character(subject)
            await ctx.send("Персонажи успешно удалены.")

    @commands.command(name="дамп")
    @commands.guild_only()
    @commands.has_role(registrar_role)
    async def dump(self, ctx, discord_id):
        rows = db.get_all_characters_raw(discord_id)
        if rows:
            output = "```"
            for row in rows:
                output += (str(row) + "\n")
            output += "```"
            await ctx.send(output)
        else:
            await ctx.send("Это не то, с чем я могу работать. Мне нужен discord_id.")

    @commands.command(name="забанить")
    @commands.guild_only()
    @commands.has_role(registrar_role)
    async def ban(self, ctx, type, subject):
        if type == "персонажа":
            db.ban_character(subject)
            await ctx.send("Персонаж успешно забанен.")
        elif type == "игрока":
            try:
                player = await commands.UserConverter().convert(ctx, str(subject))
                db.ban_player(player.id)
            except commands.UserNotFound:
                db.ban_player(subject)
            await ctx.send("Персонажи этого негодяя успешно забанены.")

    @commands.command(name="разбанить")
    @commands.guild_only()
    @commands.has_role(registrar_role)
    async def unban(self, ctx, type, subject):
        if type == "персонажа":
            db.unban_character(subject)
            await ctx.send("Персонаж успешно разбанен. Прощен. Временно.")
        elif type == "игрока":
            try:
                player = await commands.UserConverter().convert(ctx, str(subject))
                db.unban_player(player.id)
            except commands.UserNotFound:
                db.unban_player(subject)
            await ctx.send("Персонажи успешно разбанены. Амнистия!")

    @commands.command(name="проверить")
    @commands.guild_only()
    @commands.has_role(registrar_role)
    async def check(self, ctx, type, subject):
        if type == "персонажа":
            info = db.ban_character_status(subject)
            await ctx.send(info)
        elif type == "игрока":
            try:
                player = await commands.UserConverter().convert(ctx, str(subject))
                info = db.ban_player_status(player.id)
            except commands.UserNotFound:
                info = db.ban_player_status(subject)
            await ctx.send(info)

    @commands.command(name="судо-пароль")
    @commands.guild_only()
    @commands.has_role(registrar_role)
    async def sudo_password_change(self, ctx, character, password):
        db.set_new_password(character, password)
        await ctx.send("Новый пароль задан.")


def setup(bot):
    bot.add_cog(GameMasterCog(bot))
