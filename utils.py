from pathlib import Path
import asyncio
import logging

import aiosqlite
import discord

log = logging.getLogger(__name__)

TABLES = {'general', 'bump_reminder', 'counting', 'farewell_messages', 'welcome_messages'}
DATA_DIR = Path(__file__).parent / 'data'
db: aiosqlite.Connection
write_lock = asyncio.Lock()

COLOUR = 13751771

async def migrate(schema: str):
    async with aiosqlite.connect(':memory:') as ref:
        await ref.executescript(schema)
        async with ref.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ) as cursor:
            tables = await cursor.fetchall()

        for table, create_sqlite in tables:
            async with ref.execute(f'PRAGMA table_info({table})') as cursor:
                wanted = {tuple(row[1:]) for row in await cursor.fetchall()}
            async with db.execute(f'PRAGMA table_info({table})') as cursor:
                current = {tuple(row[1:]) for row in await cursor.fetchall()}
            if wanted == current:
                continue

            log.info('Migrating table %s', table)
            common = ', '.join({col[0] for col in wanted} & {col[0] for col in current})
            try:
                await db.execute('BEGIN')
                await db.execute(f'ALTER TABLE {table} RENAME TO {table}_old')
                await db.execute(create_sqlite)
                await db.execute(f'INSERT INTO {table} ({common}) SELECT {common} FROM {table}_old')
                await db.execute(f'DROP TABLE {table}_old')
                await db.commit()
            except Exception:
                await db.rollback()
                raise

async def init_db():
    global db

    DATA_DIR.mkdir(exist_ok=True)

    db = await aiosqlite.connect(DATA_DIR / 'data.db')
    db.row_factory = aiosqlite.Row

    schema = (DATA_DIR / 'schema.sql').read_text(encoding='utf-8')

    await db.executescript(schema)
    await migrate(schema)

async def get_data(guild: discord.Guild | int, table: str):
    if table not in TABLES:
        raise ValueError(f'Unknown table : {table}')

    if isinstance(guild, discord.Guild):
        guild = guild.id
    
    await db.execute(f'INSERT OR IGNORE INTO {table} (guild_id) VALUES (?)', (guild,))
    await db.commit()
    
    async with db.execute(f'SELECT * FROM {table} WHERE guild_id = ?', (guild,)) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise LookupError(f'No row in {table} for {guild}')

    return dict(row)

async def write_data(guild: discord.Guild | int, table: str, values: dict):
    if table not in TABLES:
        raise ValueError(f'Unknown table : {table}')

    if isinstance(guild, discord.Guild):
        guild = guild.id

    columns = ', '.join(f'{column} = ?' for column in values)

    async with write_lock:
        await db.execute(f'INSERT OR IGNORE INTO {table} (guild_id) VALUES (?)', (guild,))
        await db.execute(f'UPDATE {table} set {columns} WHERE guild_id = ?', (*values.values(), guild))
        await db.commit()

async def add_guild_to_db(guild: discord.Guild | int):
    if isinstance(guild, discord.Guild):
        guild = guild.id
    
    async with write_lock:
        for table in TABLES:
            await db.execute(f'INSERT OR IGNORE INTO {table} (guild_id) VALUES (?)', (guild,))
        await db.commit()

async def remove_guild_from_db(guild: discord.Guild | int):
    if isinstance(guild, discord.Guild):
        guild = guild.id
    
    async with write_lock:
        for table in TABLES:
            await db.execute(f'DELETE FROM {table} WHERE guild_id = ?', (guild,))
        await db.commit()