import logging
import json
import os
import shutil

import discord

COLOUR = 13751771

log = logging.getLogger(__name__)

def load_config(guild: discord.Guild) -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    template_path = os.path.join(script_dir, 'configs', 'template_config.json')
    target_dir = os.path.join(script_dir, 'configs', str(guild.id))
    target_file = os.path.join(target_dir, 'config.json')

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
        
    except FileNotFoundError:
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(template_path, target_file)

        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            log.warning("The bot tried to read the config file for the guild %s but it didn't exist, creating one instead.", guild.name)
            return data

    except json.JSONDecodeError:
        os.remove(target_file)
        shutil.copy2(template_path, target_file)

        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            log.warning('The bot tried to read the config file for the guild %s but it was corrupted, creating a new one instead.', guild.name)
            return data

def load_data(guild: discord.Guild) -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    template_path = os.path.join(script_dir, 'configs', 'template_data.json')
    target_dir = os.path.join(script_dir, 'configs', str(guild.id))
    target_file = os.path.join(target_dir, 'data.json')

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            return data
            
    except FileNotFoundError:
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(template_path, target_file)

        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            log.warning("The bot tried to read the data file for the guild %s but it didn't exist, creating one instead.", guild.name)
            return data

    except json.JSONDecodeError:
        os.remove(target_file)
        shutil.copy2(template_path, target_file)

        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            log.warning('The bot tried to read the data file for the guild %s but it was corrupted, creating a new one instead.', guild.name)
            return data

def write_data(guild: discord.Guild, data: dict) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    target_dir = os.path.join(script_dir, 'configs', str(guild.id))
    target_file = os.path.join(target_dir, 'data.json')

    os.makedirs(target_dir, exist_ok=True)

    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


        
