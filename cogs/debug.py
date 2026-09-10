import discord
from discord import app_commands
from discord.ext import commands

class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    debug_group = app_commands.Group(
        name='debug',
        description='Command to simulate events (dev mode only)'
    )

    @debug_group.command(name='join', description='on_member_join')
    async def debug_join(self, interaction: discord.Interaction):
        self.bot.dispatch('member_join', interaction.user)
        await interaction.response.send_message('✅ Event `on_member_join` stimulated successfully.', ephemeral=True)

    @debug_group.command(name='leave', description='on_member_leave')
    async def debug_join(self, interaction: discord.Interaction):
        self.bot.dispatch('member_leave', interaction.user)
        await interaction.response.send_message('✅ Event `on_member_leave` stimulated successfully.', ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Debug(bot))
