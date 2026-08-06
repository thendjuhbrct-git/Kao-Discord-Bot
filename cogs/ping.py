import logging

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger(__name__)

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='ping', description="Return's bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'🏓 Pong ! (~{latency} ms)')
        log.info('Command /ping used by %s in %s', interaction.user, interaction.guild)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
