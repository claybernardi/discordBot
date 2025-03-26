import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import logging

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
print("Token Loaded:", TOKEN[:5] + "..." if TOKEN else "Token NOT found")
intents = discord.Intents.all()

client = commands.Bot(command_prefix='?', intents=intents)

async def load_extensions():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await client.load_extension("cogs." + f[:-3])


async def main():
    async with client:
        await load_extensions()
        await client.start(TOKEN)



asyncio.run(main())

