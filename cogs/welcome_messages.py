import logging

import discord
from discord.ext import COLOUR, commands

from utils import load_config

log = logging.getLogger(__name__)

class Component(discord.ui.LayoutView):
    def __init__(
            self,
            title: str,
            subtitle: str,
            pfp: str
    ) -> None:
        super().__init__()

        self.container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"## {title}"),
                discord.ui.TextDisplay(content=subtitle),
                accessory=discord.ui.Thumbnail(
                    media=pfp
                ),
            ),
            accent_colour = discord.Colour(COLOUR)
        )

        self.add_item(self.container)

class WelcomeMessages(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        config = load_config(member.guild)

        enabled = bool(config.get('cogs', {}).get('welcome messages', {}).get('enabled', False))

        if not enabled: return

        raw_channel_id = config.get('cogs', {}).get('welcome messages', {}).get('channel id', None)
        if raw_channel_id is not None:
            channel_id = int(raw_channel_id)
        else:
            return log.warning('Someone joined a server but the configuration file for the server %s was invalid.', member.guild.name)

        if channel_id:
            channel = self.bot.get_channel(channel_id)

            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except Exception:
                    return log.warning("Someone joined a server but the bot couldn't retrieve the channel from the id given in the configuration file of the server %s.", member.guild.name)
        else:
            return log.warning("Someone joined a server but the bot couldn't retrieve the channel id from the configuration file of the server %s.", member.guild.name)

        raw_title = str(config.get('cogs', {}).get('welcome messages', {}).get('title', 'Welcome {member.mention} !'))
        title = raw_title.format(member=member)

        raw_subtitle = str(config.get('cogs', {}).get('welcome messages', {}).get('subtitle', 'Welcome to the {member.guild.name} Discord server'))
        subtitle = raw_subtitle.format(member=member)

        component = Component(title=title, subtitle=subtitle, pfp=str(member.display_avatar.url))
        await channel.send(view=component)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WelcomeMessages(bot))
