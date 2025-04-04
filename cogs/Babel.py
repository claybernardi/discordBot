import discord
from discord.ext import commands
from PIL import Image
import random
import io

class Babel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def babel(self, ctx):
        """Generates a 64x64 image with random RGB values for each pixel"""
        # Create a new image with RGB mode
        img = Image.new('RGB', (64, 64))
        pixels = img.load()

        # Fill each pixel with random RGB values
        for x in range(64):
            for y in range(64):
                pixels[x, y] = (
                    random.randint(0, 255),  # Red
                    random.randint(0, 255),  # Green
                    random.randint(0, 255)   # Blue
                )

        # Save the image to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Send the image as a Discord attachment
        await ctx.send(file=discord.File(buffer, filename='babel.png'))

async def setup(bot):
    await bot.add_cog(Babel(bot))
