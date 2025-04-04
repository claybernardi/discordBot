import discord
from discord.ext import commands
from PIL import Image
import random
import io

class Babel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="babel", description="Generates an image with random RGB values for each pixel", usage="{prefix}babel [width] [height]")
    async def babel(self, ctx, width: int = 64, height: int = 64):
        """Generates an image with random RGB values for each pixel
        Parameters:
        width: Width of the image (default: 64, max: 500)
        height: Height of the image (default: 64, max: 500)
        """
        # Limit maximum dimensions to prevent excessive resource usage
        width = min(max(1, width), 500)
        height = min(max(1, height), 500)

        # Create a new image with RGB mode
        img = Image.new('RGB', (width, height))
        pixels = img.load()

        # Fill each pixel with random RGB values
        for x in range(width):
            for y in range(height):
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
