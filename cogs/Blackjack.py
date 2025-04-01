from typing import Any

import discord
import random
import asyncio
from discord._types import ClientT
from numpy.f2py.symbolic import as_ne

from cogs import Currency
from discord.ext import commands

from discord import app_commands, Interaction

# Define card values (Aces can be 1 or 11)
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': [1, 11]
}
SUITS = ['♠️', '♥️', '♦️', '♣️']

# Function to create a deck
def generate_deck():
    return [f"{rank}{suit}" for rank in CARD_VALUES.keys() for suit in SUITS]

# Function to calculate hand value
def calculate_hand_value(hand):
    value, aces = 0, 0
    for card in hand:
        rank = card[:-2]  # Remove suit symbol
        if rank == 'A':
            aces += 1
        else:
            value += CARD_VALUES[rank]
    # Handle Aces (1 or 11)
    for _ in range(aces):
        value += 11 if value + 11 <= 21 else 1
    return value

class DoubleDownButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Double Down", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.player:
            return await interaction.response.send_message("This isn't your game!", ephemeral=True)
        if self.view.remaining < self.view.bet:
            return await interaction.response.send_message("You are too poor to use this button 😭", ephemeral=True)
        currency_cog = self.view.bot.get_cog("Currency")
        await currency_cog.increment_user_money(self.view.ctx, -self.view.bet)
        self.view.bet = 2*self.view.bet
        self.view.player_hand.append(self.view.deck.pop())
        self.view.game_over = True
        await self.view.dealer_turn(interaction)

# Interactive Blackjack UI
class BlackjackView(discord.ui.View):
    def __init__(self, ctx, bot, remaining, bet=0):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.player = ctx.author
        self.bet = bet
        self.remaining = remaining
        self.deck = generate_deck()
        random.shuffle(self.deck)

        # Player and dealer hands
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.game_over = False
        self.double_down_button = DoubleDownButton()
        try:
            self.add_item(self.double_down_button)
        except Exception as e:
            print(e)

    async def update_message(self, interaction):
        """ Updates the game message """
        self.remove_item(self.double_down_button)
        await interaction.response.defer()  # Prevents interaction failure

        embed = discord.Embed(title="🎰 Blackjack Game 🎰", color=discord.Color.gold())
        embed.add_field(name="Your Hand", value=", ".join(self.player_hand), inline=False)
        embed.add_field(name="Your Total", value=str(calculate_hand_value(self.player_hand)), inline=True)

        if self.game_over:
            result = self.determine_winner()
            embed.add_field(name="Dealer's Hand", value=", ".join(self.dealer_hand), inline=False)
            embed.add_field(name="Dealer Total", value=str(calculate_hand_value(self.dealer_hand)), inline=True)
            embed.add_field(name="Result", value=result[1], inline=False)
            if result[0] == 'win':
                winnings = 2*self.bet
                embed.add_field(name="Bet Info", value=f"Winnings: ${winnings}   New Total ${round(self.remaining + winnings,2)}",
                                inline=False)
            elif result[0] == 'tie':
                winnings = self.bet
                embed.add_field(name="Bet Info", value=f"Winnings: ${winnings}   New Total ${round(self.remaining + winnings,2)}",
                                inline=False)
            else:
                winnings = 0
                embed.add_field(name="Bet Info", value=f"Losses: ${self.bet}   New Total ${round(self.remaining + winnings,2)}",
                                inline=False)
            currency_cog = self.bot.get_cog("Currency")
            remaining = await currency_cog.increment_user_money(self.ctx, winnings)

            self.disable_all_buttons()
        else:
            embed.add_field(name="Dealer's Hand", value=f"{self.dealer_hand[0]}, ❓", inline=False)
        await interaction.message.edit(embed=embed, view=self)  # Properly edits message

    def determine_winner(self):
        """ Determines the game outcome """
        player_score = calculate_hand_value(self.player_hand)
        dealer_score = calculate_hand_value(self.dealer_hand)
        if player_score > 21:
            return ['loss',"💀 You busted! Dealer wins!"]
        elif dealer_score > 21:
            return ['win',"🎉 Dealer busted! You win!"]
        elif player_score == dealer_score:
            return ['tie',"🤝 It's a tie!"]
        elif player_score > dealer_score:
            #Currency.update_user_data()
            return ['win',"🎉 You win!"]
        else:
            return ['loss',"😞 Dealer wins!"]

    async def dealer_turn(self, interaction):
        """ Dealer plays their turn """
        embed = discord.Embed(title="🎰 Blackjack Game 🎰", color=discord.Color.gold())
        embed.add_field(name="Your Hand", value=", ".join(self.player_hand), inline=False)
        embed.add_field(name="Your Total", value=str(calculate_hand_value(self.player_hand)), inline=True)
        embed.add_field(name="Dealer's Hand", value=", ".join(self.dealer_hand), inline=False)
        embed.add_field(name="Dealer Total", value=str(calculate_hand_value(self.dealer_hand)), inline=True)
        await asyncio.sleep(0.5)
        await interaction.message.edit(embed=embed, view=self)

        while calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
            embed = discord.Embed(title="🎰 Blackjack Game 🎰", color=discord.Color.gold())
            embed.add_field(name="Your Hand", value=", ".join(self.player_hand), inline=False)
            embed.add_field(name="Your Total", value=str(calculate_hand_value(self.player_hand)), inline=True)
            embed.add_field(name="Dealer's Hand", value=", ".join(self.dealer_hand), inline=False)
            embed.add_field(name="Dealer Total", value=str(calculate_hand_value(self.dealer_hand)), inline=True)
            await asyncio.sleep(0.5)
            await interaction.message.edit(embed=embed, view=self)

        self.game_over = True
        await self.update_message(interaction)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            return await interaction.response.send_message("This isn't your game!", ephemeral=True)

        self.player_hand.append(self.deck.pop())
        if calculate_hand_value(self.player_hand) > 21:
            self.game_over = True  # Player busted
        await self.update_message(interaction)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            return await interaction.response.send_message("This isn't your game!", ephemeral=True)

        self.game_over = True
        await self.dealer_turn(interaction)

    def disable_all_buttons(self):
        """ Disables all buttons when game is over """
        for item in self.children:
            item.disabled = True

# Command to start Blackjack
class Blackjack(commands.Cog, name='Blackjack'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="blackjack", description="Starts a Blackjack game!")
    async def blackjack(self, ctx, bet: int = 0):
        # Create Blackjack game view and setup the game

        bet = abs(bet)
        currency_cog = self.bot.get_cog("Currency")
        balance = await currency_cog.check_money(ctx)
        if bet > balance:
            await ctx.send(embed=discord.Embed(title="Insufficient Funds",
                                               description=f"{ctx.author.mention}, please enter a bet below your balance of ${balance}",
                                               color=discord.Color.teal()))
        else:
            remaining = await currency_cog.increment_user_money(ctx, -bet)
            view = BlackjackView(ctx, self.bot, remaining, bet)
            # Build the embed to show game details
            player_hand_value = calculate_hand_value(view.player_hand)
            embed = discord.Embed(title="🎰 Blackjack Game 🎰", color=discord.Color.gold())
            embed.add_field(name="Your Hand", value=", ".join(view.player_hand), inline=False)
            embed.add_field(name="Your Total", value=str(calculate_hand_value(view.player_hand)), inline=True)
            if player_hand_value == 21:
                dealer_hand_value = calculate_hand_value(view.dealer_hand)
                embed.add_field(name="Dealer's Hand", value=f"{view.dealer_hand}", inline=False)
                embed.add_field(name="Dealer Total", value=str(calculate_hand_value(view.dealer_hand)), inline=True)
                if dealer_hand_value == 21:
                    winnings = bet
                    embed.add_field(name="Result", value="🤝 It's a tie!", inline=False)
                else:
                    winnings = 2*bet
                    embed.add_field(name="Result", value="🎉 You win!", inline=False)
                embed.add_field(name="Bet Info",
                                value=f"Winnings: ${winnings}   New Total ${round(self.remaining + winnings, 2)}",
                                inline=False)
                await currency_cog.increment_user_money(ctx, winnings)
                view.game_over = True
                view.disable_all_buttons()
            else:
                embed.add_field(name="Dealer's Hand", value=f"{view.dealer_hand[0]}, ❓", inline=False)
                embed.add_field(name="Bet Info", value=f"Bet Size: ${bet}   Money Remaining ${round(remaining,2)}", inline=False)
            # Send the embed and view to the user
            await ctx.send(embed=embed, view=view)

    #@app_commands.command(name="blackjack", description="Starts a Blackjack game!")
    #async def blackjack(interaction: discord.Interaction, bet: int = 0):
    #    """ Starts a new Blackjack game """
    #    print("Someone wants to play a game")
    #    view = BlackjackView(interaction.user, bot, bet)
    #    print("View Created")
    #    embed = discord.Embed(title="🎰 Blackjack Game 🎰", color=discord.Color.gold())
    #    print("Embed1")
    #    embed.add_field(name="Your Hand", value=", ".join(view.player_hand), inline=False)
    #    print("Embed Player")
    #    embed.add_field(name="Dealer's Hand", value=f"{view.dealer_hand[0]}, ❓", inline=False)
    #    print("Going to Send Message")
    #    await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="deduct", description="Test")
    async def deduct(self, ctx, amnt: int = 0):
        print(f"Deducting {amnt}")
        currency_cog = self.bot.get_cog("Currency")
        remaining = await currency_cog.increment_user_money(ctx, -amnt)
        print("Incremented money")
        embed=discord.Embed(title="Deduction",
                                     description=f"{ctx.author}, you deducted ${amnt} from your balance and have ${remaining}",
                                     color=discord.Color.teal())
        await ctx.send(embed=embed)

# Setup function for loading the cog
async def setup(bot):
    await bot.add_cog(Blackjack(bot))