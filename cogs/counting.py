import asyncio
import logging
import math
from decimal import Decimal, InvalidOperation

import discord
from discord.ext import commands

from utils import load_config, load_data, write_data

log = logging.getLogger(__name__)

class Counting(commands.Cog):
    def __init__ (self, bot: commands.Bot) -> None:
        self.bot = bot
        self.counting_locks: dict[int, asyncio.Lock] = {}

    def _get_lock(self, guild_id: int):
        lock = self.counting_locks.get(guild_id)
        if lock is None:
            lock = asyncio.Lock()
            self.counting_locks[guild_id] = lock
        return lock

    async def _timed_mute(self, channel: discord.abc.Messageable, member: discord.Member, duration: int) -> None:
        try:
            await channel.set_permissions(member, send_messages=False)
            await asyncio.sleep(duration)
            await channel.set_permissions(member, send_messages=None)
        except Exception:
            log.exception('An error occurred while unmuting %s in %s.', member.name, member.guild.name)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        async with self._get_lock(message.guild.id):
            if message.author.bot: return

            config = load_config(guild=message.guild)

            enabled = bool(config.get('cogs', {}).get('counting', {}).get('enabled', False))

            if not enabled: return

            raw_channel_id = config.get('cogs', {}).get('counting', {}).get('channel id', None)
            if raw_channel_id is not None:
                channel_id = int(raw_channel_id)
            else:
                return log.warning('Someone sent a message but the configuration file for the server %s was invalid.', message.guild.name)

            if channel_id:
                channel = self.bot.get_channel(channel_id)

                if channel is None:
                    try:
                        channel = await self.bot.fetch_channel(channel_id)
                    except Exception:
                        return log.warning("Someone sent a message but the bot couldn't retrieve the channel from the id given in the configuration file of the server %s.", message.guild.id)
            else:
                return log.warning("Someone sent a message but the bot couldn't retrieve the channel id from the configuration file of the server %s.", message.guild.id)
            
            if message.channel != channel: return

            allow_floating_number = bool(config.get('cogs', {}).get('counting', {}).get('allow floating numbers', False))
            checkpoints = config.get('cogs', {}).get('counting', {}).get('checkpoints', {})
            mute_user_who_break_the_chain = config.get('cogs', {}).get('counting', {}).get('mute users who break the chain', {})

            data = load_data(guild=message.guild)

            last_number = float(data.get('counting', {}).get('last number', 0))
            raw_last_user_id = data.get('counting', {}).get('last user id', 0)
            if raw_last_user_id is not None:
                last_user_id = int(raw_last_user_id)
            else:
                last_user_id = None

            raw_number = message.content.strip().replace(',', '.').replace('`', '')

            try:
                number = float(raw_number)
            except ValueError:
                return

            try:
                exact_number = Decimal(raw_number)
            except InvalidOperation:
                return

            was_rounded = Decimal(str(number)) != exact_number

            if was_rounded:
                await message.channel.send(f'Your number had too many decimal places and was rounded to {number}.')

            will_be_checkpoint = None
            previous_checkpoint = None

            if bool(checkpoints.get('enabled', False)):
                distance = int(checkpoints.get('distance between checkpoints', 100))

                will_be_checkpoint = number.is_integer() and int(number) % distance == 0
                previous_checkpoint = math.floor(last_number / distance) * distance

            if allow_floating_number:
                is_valid = last_number < number <= last_number + 1
            else:
                is_valid = number == last_number+1

            if is_valid and int(message.author.id) != last_user_id:
                await message.add_reaction('✅')

                if number == 100: await message.add_reaction('💯')

                if will_be_checkpoint: await message.add_reaction('🚩')

                data['counting']['last number'] = number
                data['counting']['last user id'] = message.author.id

                write_data(message.guild, data)

            elif not is_valid and int(message.author.id) != last_user_id:
                await message.add_reaction('❌')

                if bool(mute_user_who_break_the_chain.get('enabled', False)):
                    duration = int(mute_user_who_break_the_chain.get('duration', 3600))
                    asyncio.create_task(self._timed_mute(message.channel, message.author, duration))

                if bool(checkpoints.get('enabled', False)):
                    data['counting']['last number'] = previous_checkpoint
                    data['counting']['last user id'] = None

                    write_data(message.guild, data)

                    await message.channel.send(f'{message.author.mention} made a mistake: the count reverted to the previous checkpoint.\n-# The next number is {previous_checkpoint + 1}')   
                else:
                    data['counting']['last number'] = 0
                    data['counting']['last user id'] = None

                    write_data(message.guild, data)

                    await message.channel.send(f'{message.author.mention} made a mistake: the count has been reset.\n-# The next number is 1')

            elif int(message.author.id) == last_user_id:
                await message.channel.send(f'{message.author.mention} you cannot count twice in a row.\n-# The next number is {last_number + 1}')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Counting(bot))
