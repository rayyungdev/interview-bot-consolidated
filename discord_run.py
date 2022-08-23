import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import sys 
import asyncio
sys.path.append('./bot_model')

intents = discord.Intents.default()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix = '!', intents = intents)

@client.event
async def on_ready():
    print('Bot Successfully Connected')
    
@client.command(brief = 'load cog')
@commands.has_guild_permissions(administrator = True)
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')

@client.command(brief = 'unload cog')
@commands.has_guild_permissions(administrator = True)
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load_extensions()
        await client.start(TOKEN)

asyncio.run(main())