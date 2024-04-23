# bot.py or main bot file
import discord
from discord.ext import commands
from JobHuntingCog import JobHuntingCog  # Make sure to import your cog
from typing import List
from gh_parser.JobPosting import JobPosting


class JobHuntingBot(commands.Bot):
    def __init__(
        self,
        filename: str,
        channel_id: int,
        job_postings: List[JobPosting],
        command_prefix="!",
        intents=discord.Intents.all(),
    ):
        self.filename = filename
        self.channel_id = channel_id
        self.job_postings = job_postings
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        # Load your cogs here
        await self.add_cog(JobHuntingCog(self, self.channel_id, self.job_postings))
        # Setup actions like sending a startup message can also go here
        print("Bot setup complete!")
