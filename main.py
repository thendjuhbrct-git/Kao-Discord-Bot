import argparse
import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise RuntimeError(
        'DISCORD_TOKEN missing. Create a .env file with DISCORD_TOKEN=...'
    )

COGS_DIR = Path(__file__).parent / 'cogs'
TEST_GUILD_ID = int(os.getenv('TEST_GUILD_ID') or 0)

log = logging.getLogger('bot.main')

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Launch the Discord bot')
    parser.add_argument(
        '--dev', 
        action='store_true', 
        help='launch the bot in developer mode to, among other things, avoid Discord rate limits and unlock debugging commands during testing or development',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='show all the logs (DEBUG) and full tracebacks',
    )
    return parser.parse_args()

def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log', encoding='utf-8'),
        ],
        force=True
    )
    logging.getLogger('discord').setLevel(logging.DEBUG if verbose else logging.WARNING)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Bot(commands.AutoShardedBot):
    def __init__(self, dev_mode: bool = False) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None,
        )
        self.dev_mode = dev_mode

    async def setup_hook(self) -> None:
        await self._load_cogs()

        if self.dev_mode:
            if not TEST_GUILD_ID:
                log.warning('Developer mode enabled but TEST_GUILD_ID not in .env, using global sync')
                synced = await self.tree.sync()
                log.info('%s commands synced.', len(synced))
            else:
                guild = discord.Object(id=TEST_GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                log.info('Developer mode : %s commands synced only on the test guild', len(synced))
        else:
            synced = await self.tree.sync()
            log.info('%s commands synced.', len(synced))

    async def _load_cogs(self) -> None:
        if not COGS_DIR.exists():
            log.warning("Folder cogs/ doesn't exist, no cog loaded.")
            return

        for path in sorted(COGS_DIR.glob("*.py")):
            if path.stem.startswith("_"):
                continue

            extension = f'cogs.{path.stem}'
            try:
                await self.load_extension(extension)
                log.info('Cog loaded : %s', extension)
            except Exception:
                log.exception('Failed to load cog : %s', extension)

    async def on_ready(self) -> None:
        log.info(
            'Connected as %s (id=%s) — %d server(s), %d shard(s)',
            self.user,
            self.user.id if self.user else '?',
            len(self.guilds),
            self.shard_count or 1,
        )

async def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)

    bot = Bot(dev_mode=args.dev)
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    args = parse_args()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Stopping the bot (manual interruption).')
    except Exception:
        if args.verbose:
            raise
        else:
            log.error('Fatal error occured, rerty with -v for details')
