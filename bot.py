import asyncio
import os
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!\n')

def load_cogs():
    '''
    The code in this function is executed whenever the bot will start.
    '''
    for file in os.listdir(f'./cogs'):
        if file.endswith('.py'):
            extension = file[:-3]
            try:
                bot.load_extension(f'cogs.{extension}')
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f'{type(e).__name__}: {e}'
                print(f'Failed to load extension {extension}\n{exception}')

load_cogs()
bot.run(TOKEN)