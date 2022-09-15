import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot

class General(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(hidden = True)
    async def ping(self, ctx):
        await ctx.send('pong')
    
def setup(bot: Bot):
    bot.add_cog(General(bot))