import logging
import os
import shutil

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

class Configs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)

        target_dir = os.path.join(root_dir, 'configs', str(guild.id))

        template_path = os.path.join(root_dir, 'configs', 'template.json')
        destination_path = os.path.join(target_dir, 'config.json')

        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(template_path, destination_path)

            log.info('The bot has been added to the guild %s; configuration file successfully created.', guild.name)
        except Exception as e:
            log.warning('The bot was added to the server %s, but an error occurred while creating the configuration file: %s', guild.name, e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)

        target_dir = os.path.join(root_dir, 'configs', str(guild.id))

        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)

                log.info('The bot has been removed from the guild %s; configuration file successfully deleted.', guild.name)
            except Exception as e:
                log.warning('The bot was remover from the guild %s, but an error occured while deleting the configuration file: %s', guild.name, e)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Configs(bot))
