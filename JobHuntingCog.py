# job_hunting_cog.py
from discord import Embed
from discord.ext import commands
from gh_parser.JobPosting import JobPosting
from typing import List


class JobHuntingCog(commands.Cog):
    def __init__(self, logger, bot, channel_id: int, job_postings: List[JobPosting]):
        self.logger = logger
        self.bot = bot
        self.channel_id = channel_id
        self.job_postings = job_postings

    async def send_job_postings(self, channel):
        try:
            if channel is None:
                raise Exception(f"Channel with ID {self.channel_id} not found.")
        except Exception as e:
            self.logger.error(e)
            raise

        await channel.send("Hunting for jobs...")

        for posting in self.job_postings:
            # Create a Discord Embed to display the job posting nicely
            embed = Embed(
                title=" 🚨🚨🚨\t New Job Posting \t 🚨🚨🚨", color=0x00FF00
            )  # Creates a green embed
            embed.add_field(
                name="🏢 Company",
                value=(
                    f"[{posting.company_name}]({posting.career_site})\t"
                    if posting.career_site
                    else posting.company_name
                ),
                inline=False,
            )
            embed.add_field(
                name="📍 Location(s)", value="\n".join(posting.locations), inline=True
            )
            embed.add_field(
                name="🛂 Sponsorship Available",
                value=f"{posting.has_sponsorship}\t",
                inline=False,
            )
            embed.add_field(
                name="📅 Date Posted", value=f"{posting.date_posted}\t", inline=False
            )

            # Adding roles as fields
            embed.add_field(name="🧑‍💻 Role(s)", value="", inline=False)
            for role, link in posting.roles.items():
                embed.add_field(name="", value=f"[{role}]({link})", inline=True)

            await channel.send(embed=embed)
        await self.bot.close()  # TODO - Hacky way to turn off bot for a bit

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Job Hunting Cog is ready!")
        channel = self.bot.get_channel(self.channel_id)
        await self.send_job_postings(channel)
