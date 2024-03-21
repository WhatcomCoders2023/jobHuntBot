# bot.py or main bot file
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from JobHuntingCog import JobHuntingCog  # Make sure to import your cog


class JobHuntingBot(commands.Bot):
    def __init__(self, filename: str, channel_id: int, command_prefix="!", intents=discord.Intents.all()):
        self.filename = filename
        self.channel_id = channel_id
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        # Load your cogs here
        await self.add_cog(JobHuntingCog(self, self.filename, self.channel_id))
        # Setup actions like sending a startup message can also go here
        print('Bot setup complete!')
