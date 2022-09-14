import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot

class Hidden(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(hidden=True)
    async def say(self, ctx, msg, channel: int = 1004062992301830278):
        channel = self.bot.get_channel(channel)
        await channel.send(msg)

def setup(bot: Bot):
    bot.add_cog(Hidden(bot))