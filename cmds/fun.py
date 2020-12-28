from discord.ext import commands

import config_values
from utility.discord_util import role_converter


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    users_with_player_role_raw = []
    users_with_player_role_name = []

    @commands.has_role(config_values.admin_role)
    @commands.command(name="обновикэш", hidden=True)
    async def refill_cache(self, ctx):
        role = await role_converter.convert(ctx, str(config_values.player_role_id))
        raw_list = role.members
        self.users_with_player_role_raw = raw_list
        self.users_with_player_role_name = [user.display_name for user in raw_list]
        await ctx.send("Кэш обновлен.")


def setup(bot):
    bot.add_cog(FunCog(bot))
