import random

from discord.ext import commands

import constants
from utility.discord_util import role_converter


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    users_with_player_role_raw = []
    users_with_player_role_name = []

    @commands.has_role(constants.admin_role)
    @commands.command(name="обновикэш", hidden=True)
    async def refill_cache(self, ctx):
        role = await role_converter.convert(ctx, str(constants.player_role_id))
        raw_list = role.members
        self.users_with_player_role_raw = raw_list
        self.users_with_player_role_name = [user.display_name for user in raw_list]
        await ctx.send("Кэш обновлен.")

    @commands.command(name="скажикто")
    async def pick_random_user(self, ctx, *args):
        pick = random.choice(self.users_with_player_role_name)
        args = " ".join(args)
        await ctx.send(pick + " " + args)

    @commands.Cog.listener("on_message")
    async def pick_random_user_on_word(self, msg):
        ctx = await self.bot.get_context(msg)
        message = msg.content
        if "кто-то" in message:
            temp_list = message.split("кто-то")
            pick = random.choice(self.users_with_player_role_name)
            await ctx.send(temp_list[0] + pick + temp_list[1])


def setup(bot):
    bot.add_cog(FunCog(bot))
