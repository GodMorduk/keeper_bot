from discord.ext import commands

import config_values
import handlers.mongo_handler as mng
import utility.mongo_util as mngu
from utility.discord_util import role_converter, user_converter


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

    @commands.has_role(config_values.admin_role)
    @commands.command(name="выдать", hidden=True)
    async def give_reward(self, ctx, user, reward, amount="+1"):
        user = await user_converter.convert(ctx, user)

        mng.reward_changer(user.id, reward, amount)

        if str(amount).startswith("-"):
            await ctx.send(f"Партия недовольна вами, <@{user.id}>! Вы теряете {amount} {reward}!")
        elif str(amount).startswith("+"):
            await ctx.send(f"Партия довольна вами, <@{user.id}>! Вы получаете {amount} {reward}!")
        else:
            await ctx.send(f"Партия постановила установить ваши {reward} на {amount}, <@{user.id}>!")

    @commands.has_role(config_values.admin_role)
    @commands.command(name="кредит", hidden=True)
    async def give_credit(self, ctx, user, amount):
        user = await user_converter.convert(ctx, user)

        mng.social_credit_changer(user.id, amount)

        if str(amount).startswith("-"):
            await ctx.send(f"Партия недовольна вами, <@{user.id}>! Вы теряете {amount} очков социального кредита!")
        elif str(amount).startswith("+"):
            await ctx.send(f"Партия довольна вами, <@{user.id}>! Вы получаете {amount} очков социального кредита!")
        else:
            await ctx.send(f"Партия постановила установить ваши очки социального кредита на {amount}, <@{user.id}>!")

    @commands.command(name="гражданин", hidden=True)
    async def check_citizen(self, ctx, user):
        user = await user_converter.convert(ctx, user)
        await ctx.send(embed=mngu.beautify_citizen_info(mng.get_citizen_info(user.id)))


def setup(bot):
    bot.add_cog(FunCog(bot))
