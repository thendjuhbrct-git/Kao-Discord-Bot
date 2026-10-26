CREATE TABLE IF NOT EXISTS general (
    guild_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT "en",
    timezone TEXT DEFAULT "UTC"
);

CREATE TABLE IF NOT EXISTS bump_reminder (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    enabled INTEGER NOT NULL DEFAULT 0,
    ping_role TEXT,
    next_bump INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS counting (
    guild_id INTEGER PRIMARY KEY,
    allow_decimals INTEGER NOT NULL DEFAULT 0,
    channel_id INTEGER,
    checkpoint_enabled INTEGER NOT NULL DEFAULT 0,
    checkpoint_distance INTEGER NOT NULL DEFAULT 100,
    enabled INTEGER NOT NULL DEFAULT 0,
    last_number INTEGER NOT NULL DEFAULT 0,
    last_user_id INTEGER
);

CREATE TABLE IF NOT EXISTS farewell_messages (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    enabled INTEGER NOT NULL DEFAULT 0,
    ignore_bots INTEGER NOT NULL DEFAULT 1,
    subtitle TEXT DEFAULT "See you soon on {member.guild.name}",
    title TEXT DEFAULT "Goodbye {member.mention}"
);

CREATE TABLE IF NOT EXISTS welcome_messages (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    enabled INTEGER NOT NULL DEFAULT 0,
    ignore_bots INTEGER NOT NULL DEFAULT 1,
    subtitle TEXT DEFAULT "Welcome to the {member.guild.name} Discord server",
    title TEXT DEFAULT "Welcome {member.mention} !"
);