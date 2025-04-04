import discord
from discord.ext import commands
from PIL import Image
import random
import io
import asyncio

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

        # Generate and send the image
        file = self.generate_babel_image(width, height)
        await ctx.send(file=file)

    def generate_babel_image(self, width: int, height: int) -> discord.File:
        """Helper method to generate a babel image"""
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
        return discord.File(buffer, filename='babel.png')

    class StopButton(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.stopped = False

        @discord.ui.button(label='Stop', style=discord.ButtonStyle.danger)
        async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.stopped = True
            button.disabled = True
            await interaction.response.edit_message(view=self)

    @commands.command(name="babel_stream", description="Continuously generates new babel images until stopped", usage="{prefix}babel_stream [width] [height] [delay]")
    async def babel_stream(self, ctx, width: int = 64, height: int = 64, delay: float = 1.0):
        """Continuously generates new babel images until stopped
        Parameters:
        width: Width of the image (default: 64, max: 500)
        height: Height of the image (default: 64, max: 500)
        delay: Delay between updates in seconds (default: 1.0, min: 0.5)
        """
        # Limit maximum dimensions and minimum delay
        width = min(max(1, width), 500)
        height = min(max(1, height), 500)
        delay = max(0.5, delay)

        view = self.StopButton()
        file = self.generate_babel_image(width, height)
        message = await ctx.send(file=file, view=view)

        while not view.stopped:
            await asyncio.sleep(delay)
            if not view.stopped:  # Check again after delay
                file = self.generate_babel_image(width, height)
                await message.edit(attachments=[file], view=view)

        await message.edit(content="Stream stopped!", view=None)

async def setup(bot):
    await bot.add_cog(Babel(bot))
    print('Babel cog has loaded')
