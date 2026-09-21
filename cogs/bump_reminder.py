import asyncio
import logging
import time

import discord
from discord.ext import commands

from utils import COLOUR, load_config, load_data, write_data

COOLDOWN = 7200
DISBOARD_ID = 123456789012345678

log = logging.getLogger(__name__)

class Components(discord.ui.LayoutView):
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="# ⏰ It's time to </bump:947088344167366698> the server again."),
        accent_colour=discord.Colour(COLOUR)
    )

class BumpReminder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.tasks: dict[int, asyncio.Task] = {}

    async def cog_load(self) -> None:
        self.restore_task = asyncio.create_task(self.restore())

    async def cog_unload(self) -> None:
        self.restore_task.cancel()
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()

    async def restore(self) -> None:
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            when = load_data(guild=guild).get('bump', {}).get('next bump')
            if when is not None:
                self.schedule(guild, when)
    
    def schedule(self, guild: discord.Guild, when: float) -> None:
        old = self.tasks.pop(guild.id, None)
        if old:
            old.cancel()
        self.tasks[guild.id] = asyncio.create_task(self.remind(guild, when))

    async def remind(self, guild: discord.Guild, when: float) -> None:
        await asyncio.sleep(max(0, when - time.time()))

        config = load_config(guild=guild)
        data = load_data(guild=guild)
        
        data['bump']['next bump'] = None
        write_data(guild, data)
        
        self.tasks.pop(guild.id, None)

        raw_channel_id = config.get('cogs', {}).get('bump reminder', {}).get('channel id', None)
        if raw_channel_id is not None:
            channel_id = int(raw_channel_id)
        else:
            return log.warning('Someone sent a message but the configuration file for the server %s was invalid.', message.guild.name)
        
        if channel_id:
            channel = self.bot.get_channel(channel_id)

            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except:
                    return log.warning("Someone sent a message but the bot couldn't retrieve the channel from the id given in the configuration file of the server %s.", message.guild.id)
        else:
            return log.warning("Someone sent a message but the bot couldn't retrieve the channel id from the confiuration file of the server %s.", message.guild.id)
        
        await channel.send(view=Components())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None: return
        if not message.author.id == DISBOARD_ID: return

        enabled = bool(config.get('cogs', {}).get('bump reminder', {}).get('enabled', False))

        if not enabled: return

        data = load_data(guild=message.guild)
        when = int(time.time()) + COOLDOWN

        data['bump']['next bump'] = when
        write_data(message.guild, data)

        self.schedule(message.guild, when)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BumpReminder(bot))
