import asyncio
import json
import logging
import time

import discord
from discord.ext import commands

from utils import COLOUR, DISBOARD_BUMP_COMMAND_ID, DISBOARD_COOLDOWN, DISBOARD_ID, get_data, write_data

log = logging.getLogger(__name__)

class Components(discord.ui.LayoutView):
    def __init__(
            self,
            role: str | None = None
    ) -> None:
        super().__init__()

        self.container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"**⏰ It's time to </bump:{DISBOARD_BUMP_COMMAND_ID}> the server again.**"),
            accent_colour=discord.Colour(COLOUR)
        )

        if role:
            self.add_item(discord.ui.TextDisplay(content=role))
        self.add_item(self.container)

class BumpReminder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.tasks: dict[int, asyncio.Task] = {}

    async def cog_load(self) -> None:
        self.restore_tasks = asyncio.create_task(self.restore())

    async def cog_unload(self) -> None:
        self.restore_tasks.cancel()
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()

    async def restore(self) -> None:
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            when = (await get_data(guild, 'bump_reminder'))['next_bump']
            if when:
                self.schedule(guild, when)

    def schedule(self, guild: discord.Guild, when: float) -> None:
        old = self.tasks.pop(guild.id, None)
        if old:
            old.cancel()
        self.tasks[guild.id] = asyncio.create_task(self.remind(guild, when))

    async def remind(self, guild: discord.Guild, when: float) -> None:
        await asyncio.sleep(max(0, when - time.time()))

        row = await get_data(guild, 'bump_reminder')
        await write_data(guild, 'bump_reminder', {'next_bump': None})

        self.tasks.pop(guild.id, None)
        if not row['enabled']: return

        raw_channel_id = row['channel_id']
        if not raw_channel_id: return

        channel = self.bot.get_channel(int(raw_channel_id))
        if not isinstance(channel, discord.abc.Messageable): return

        raw_ping_ids = json.loads(row['pings'])
        pings = [guild.get_role(ping_id) for ping_id in raw_ping_ids]
        pings = [role for role in pings if role is not None]

        try:
            await channel.send(view=Components(role=', '.join(role.mention for role in pings)))
        except discord.HTTPException:
            log.exception('Failed to send the bump reminder in guild %s (id: %s)', guild.name, guild.id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None: return
        if not message.author.id == DISBOARD_ID: return

        row = await get_data(message.guild, 'bump_reminder')
        enabled = bool(row['enabled'])

        if not enabled: return

        interaction = message.interaction
        if interaction is None or interaction.name != 'bump': return

        when = int(time.time()) + DISBOARD_COOLDOWN

        await write_data(message.guild, 'bump_reminder', {'next_bump': when})

        self.schedule(message.guild, when)
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BumpReminder(bot))