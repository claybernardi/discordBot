import discord
import json
from discord.ext import commands
import asyncio
import logging
import time
from make_booster import make_clayton_booster, get_sets
from cogs.Currency import Currency  # Import the Currency cog

CARD_DATA = "user_cards.json"  # File to store user card data


def load_card_data(location):
    """Loads user card data from a JSON file."""
    try:
        with open(location, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_card_data(data, location):
    """Saves user card data to a JSON file."""
    with open(location, "w") as f:
        json.dump(data, f, indent=4)


def add_cards_to_user(card_data, user_id, cards):
    """Adds a list of cards to a user's collection."""
    user_id = str(user_id)
    if user_id not in card_data:
        card_data[user_id] = []
    card_data[user_id].extend(cards)


def get_user_cards(card_data, user_id):
    """Retrieves a user's card collection."""
    user_id = str(user_id)
    return card_data.get(user_id, [])


def remove_card_from_user(card_data, user_id, card_to_remove):
    """Removes a specific card from a user's collection."""
    user_id = str(user_id)
    if user_id in card_data:
        try:
            card_data[user_id].remove(card_to_remove)
            return True  # Card removed successfully
        except ValueError:
            return False # Card not found
    return False  # User not found


class MagicBooster(discord.ui.View):
    def __init__(self, ctx, bot, booster, card_data):
        super().__init__()
        self.booster = booster
        self.count = 0
        self.user = ctx.author
        self.bot = bot
        self.card_data = card_data
        self.ctx = ctx  # add ctx to the view
        add_cards_to_user(self.card_data, self.user.id, self.booster) # Add all cards to collection on creation
        save_card_data(self.card_data, CARD_DATA)

    async def update_message(self, interaction):
        await interaction.response.defer()
        if not self.booster:
            await interaction.message.edit(content="You have sold all the cards in this pack!", view=None)
            return
        current_card = self.booster[self.count]
        try:
            price = float(current_card['prices']['usd'])
        except Exception as e:
            price = 0
            print(f"price issue {e}")
        try:
            embed = discord.Embed(title=f'{self.user} Here is your pack',
                                  description=f"{current_card['name']}: ${price} - Card [{self.count + 1}/{len(self.booster)}]",
                                  color=discord.Color.teal())
            embed.set_image(url=current_card['image_uris']['normal'])
        except Exception as e:
            print(f"Image issue {e}")
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.green)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your pack!", ephemeral=True)
        self.count -= 1
        if self.count < 0:
            self.count = len(self.booster) - 1
        await self.update_message(interaction)

    @discord.ui.button(label="💰", style=discord.ButtonStyle.red)
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # defer the interaction
        current_card = self.booster[self.count]
        try:
            price = float(current_card['prices']['usd'])
        except Exception as e:
            price = 0
            print(f"price issue {e}")

        currency_cog = self.bot.get_cog("Currency")
        await currency_cog.increment_user_money(self.ctx, price)  # use self.ctx instead of interaction
        await interaction.followup.send(f"You sold {current_card['name']} for ${price}!",
                                        ephemeral=True)  # use interaction.followup instead of interaction.response
        remove_card_from_user(self.card_data, self.user.id, current_card) #remove from collection
        save_card_data(self.card_data, CARD_DATA)
        self.booster.remove(current_card)
        if self.count >= len(self.booster):
            self.count = len(self.booster) - 1
        await self.update_message(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your pack!", ephemeral=True)
        self.count += 1
        if self.count > len(self.booster) - 1:
            self.count = 0 #loop back to the beginning
        await self.update_message(interaction)


class CollectionView(discord.ui.View):
    def __init__(self, ctx, bot, user_cards):
        super().__init__()
        self.user_cards = user_cards
        self.count = 0
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx

    async def update_message(self, interaction):
        await interaction.response.defer()
        if not self.user_cards:
            await interaction.message.edit(
                embed=discord.Embed(title="Your Collection", description="Your collection is empty!",
                                    color=discord.Color.red()), view=None)
            return
        try:
            card = self.user_cards[self.count]
            embed = discord.Embed(title=f"{self.user}'s Collection",
                                  description=f"{card['name']} ({card['set'].upper()}) - Card [{self.count + 1}/{len(self.user_cards)}]",
                                  color=discord.Color.teal())
            embed.set_image(url=card['image_uris']['normal'])
        except Exception as e:
            print(f"Image issue {e}")
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.green)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your collection!", ephemeral=True)
        self.count -= 1
        if self.count < 0:
            self.count = len(self.user_cards) - 1
        await self.update_message(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your collection!", ephemeral=True)
        self.count += 1
        if self.count > len(self.user_cards) - 1:
            self.count = 0
        await self.update_message(interaction)


class Magic(commands.Cog, name="Magic"):
    def __init__(self, bot):
        self.bot = bot
        self.card_data = load_card_data(CARD_DATA)

    @commands.command(name='mtg', help="testing")
    async def mtg(self, ctx):
        embed = discord.Embed(title=f"Here is a test image", color=discord.Color.teal())
        embed.set_image(
            url="https://cards.scryfall.io/normal/front/2/3/237568e3-7331-4bbb-a091-a766723134fc.jpg?1738356223")
        await ctx.send(embed=embed)

    @commands.command(name='booster', help=" - Open a booster pack")
    async def booster(self, ctx, set_code):
        try:
            pack = make_clayton_booster(set_code, 'play')
        except Exception as e:
            await ctx.send(f"Error: {e}")
            return

        try:
            price = float(pack[0]['prices']['usd'])
        except Exception as e:
            price = 0
            print(f"price issue {e}")
        view = MagicBooster(ctx, self.bot, pack, self.card_data)
        embed = discord.Embed(title=f'{ctx.author} Here is your pack',
                              description=f"{pack[0]['name']}: ${price} - Card [1/14]",
                              color=discord.Color.teal())
        embed.set_image(url=pack[0]['image_uris']['normal'])
        await ctx.send(embed=embed, view=view)

    @commands.command(name='test_booster', help=" - Open a booster pack")
    async def test_booster(self, ctx, set_code):
        try:
            pack = make_clayton_booster(set_code, 'play')
        except Exception as e:
            await ctx.send(f"Error: {e}")
            return
        cards = ''
        for card in pack:
            cards += f"{card['image_uris']['normal']} \n"

        embed = discord.Embed(title='Here is your pack', description=cards, color=discord.Color.teal())
        await ctx.send(embed=embed)

    # Command to list all MTG sets and their setcodes, uses get_sets() from make_booster.py
    @commands.command(name='sets', help=" - List all MTG sets and their setcodes")
    async def sets(self, ctx):
        sets = get_sets()
        set_list = ''
        for key, value in sets.items():
            set_list += f"{key}: {value}\n"

        # paginator stuff cause string too long cause too many MTG sets
        p = commands.Paginator()
        for line in set_list.splitlines():
            p.add_line(line)
        for page in p.pages:
            await ctx.send(page)

    @commands.command(name='collectionlist', help=' - Shows a list of all cards in your current collection')
    async def collectionlist(self, ctx):
        user_id = ctx.author.id
        user_cards = get_user_cards(self.card_data, user_id)
        if not user_cards:
            await ctx.send(embed=discord.Embed(title="Your Collection", description="Your collection is empty!",
                                               color=discord.Color.red()))
            return

        card_list = ""
        for card in user_cards:
            card_list += f"{card['name']} ({card['set'].upper()})\n"

        # Paginator stuff for when collection gets loooong
        p = commands.Paginator()
        for line in card_list.splitlines():
            p.add_line(line)
        for page in p.pages:
            await ctx.send(page)

    @commands.command(name='collection', help=' - Shows your current card collection')
    async def collection(self, ctx):
        user_id = ctx.author.id
        user_cards = get_user_cards(self.card_data, user_id)
        if not user_cards:
            await ctx.send(embed=discord.Embed(title="Your Collection", description="Your collection is empty!",
                                               color=discord.Color.red()))
            return
        view = CollectionView(ctx, self.bot, user_cards)
        card = user_cards[0]
        embed = discord.Embed(title=f"{ctx.author}'s Collection",
                              description=f"{card['name']} ({card['set'].upper()}) - Card [1/{len(user_cards)}]",
                              color=discord.Color.teal())
        embed.set_image(url=card['image_uris']['normal'])
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Magic(bot))
