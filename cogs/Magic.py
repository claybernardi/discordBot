import discord
import json
from discord.ext import commands
import asyncio
import logging
import time
from make_booster import make_clayton_booster, get_sets


class MagicBooster(discord.ui.View):
    def __init__(self, ctx, bot, booster):
        super().__init__()
        self.booster = booster
        self.count = 0
        self.user = ctx.author

    async def update_message(self, interaction):
        await interaction.response.defer()
        try:
            price = float(self.booster[self.count]['prices']['usd'])
        except Exception as e:
            price = 0
            print(f"price issue {e}")
        try:
            embed = discord.Embed(title=f'{self.user} Here is your pack', description=f"{self.booster[self.count]['name']}: ${price} - Card [{self.count+1}/14]",color=discord.Color.teal())
            embed.set_image(url=self.booster[self.count]['image_uris']['normal'])
        except Exception as e:
            print(f"Image issue {e}")
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.green)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your pack!", ephemeral=True)
        self.count -= 1
        if self.count<0:
            return await interaction.response.send_message("That is the beginning of the pack!", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="💰", style=discord.ButtonStyle.red)
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await interaction.response.send_message("Feature implemented yet 😔", ephemeral=True)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your pack!", ephemeral=True)
        self.count += 1
        if self.count>13:
            return await interaction.response.send_message("That is the end of the pack!", ephemeral=True)
        await self.update_message(interaction)


class Magic(commands.Cog, name="Magic"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mtg', help="testing")
    async def mtg(self, ctx):
        embed = discord.Embed(title=f"Here is a test image", color=discord.Color.teal())
        embed.set_image(url="https://cards.scryfall.io/normal/front/2/3/237568e3-7331-4bbb-a091-a766723134fc.jpg?1738356223")
        await ctx.send(embed=embed)

    @commands.command(name='booster', help=" - Open a booster pack")
    async def booster(self,ctx, set_code):
        pack = make_clayton_booster(set_code, 'play')
        try:
            price = float(pack[0]['prices']['usd'])
        except Exception as e:
            price = 0
            print(f"price issue {e}")
        view = MagicBooster(ctx, self.bot, pack)
        embed = discord.Embed(title=f'{ctx.author} Here is your pack',description=f"{pack[0]['name']}: ${price} - Card [1/14]", color=discord.Color.teal())
        embed.set_image(url=pack[0]['image_uris']['normal'])
        await ctx.send(embed=embed, view=view)

    @commands.command(name='test_booster', help=" - Open a booster pack")
    async def test_booster(self, ctx, set_code):
        pack = make_clayton_booster(set_code, 'play')
        cards = ''
        for card in pack:
            cards += f"{card['image_uris']['normal']} \n"

        embed = discord.Embed(title='Here is your pack', description= cards, color=discord.Color.teal())
        await ctx.send(embed=embed)

    #Command to list all MTG sets and their setcodes, uses get_sets() from make_booster.py
    @commands.command(name='sets', help=" - List all MTG sets and their setcodes")
    async def sets(self, ctx):
        sets = get_sets()
        set_list = ''
        for key, value in sets.items():
            set_list += f"{key}: {value}\n"

        #paginator stuff cause string too long cause too many MTG sets
        p = commands.Paginator()
        for line in set_list.splitlines():
            p.add_line(line)
        for page in p.pages:
            await ctx.send(page)


async def setup(bot):
    await bot.add_cog(Magic(bot))