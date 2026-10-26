import logging

import discord
from discord.ext import commands

from utils import add_guild_to_db, remove_guild_from_db

log = logging.getLogger(__name__)

class Configs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await add_guild_to_db(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await remove_guild_from_db(guild)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Configs(bot))