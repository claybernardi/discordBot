import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
print("Token Loaded:", TOKEN[:5] + "..." if TOKEN else "Token NOT found")
intents = discord.Intents.all()
a = False

client = commands.Bot(command_prefix='?', intents=intents)
@client.event
async def on_ready():
    print("Bot is Ready")
    if a is True:
        try:
            # Automatically sync slash commands with Discord
            synced = await client.tree.sync()
            await client.tree.sync(guild=discord.Object(id=554026246451888149))
            await client.tree.sync(guild=discord.Object(id=1035671567239225354))
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)
async def load_extensions():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await client.load_extension("cogs." + f[:-3])


async def main():
    async with client:
        await load_extensions()
        await client.start(TOKEN)


asyncio.run(main())

