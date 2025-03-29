import discord
import json
from discord.ext import commands
import asyncio
import logging
import time

USER_DATA = "users.json"


def load_user_data(location):
    try:
        with open(location, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    print("loaded")


def create_new_user(database, user_id):
    database[user_id] = {"money": 100, "last_join": None}
    print("Created a new user")

def update_user_data(database, user_id, field, data):
    if user_id not in database:
        create_new_user(database=database, user_id=user_id)
    database[user_id][field] = data
    print(f"Updated Data")

def update_money(data, rate, user_id, current_time):
    money_earned = ((current_time - data[user_id]["last_join"]) / 60) * rate
    print(f"Money Earned {money_earned}")
    total_money = round(data[user_id]["money"] + money_earned, 2)
    print(f"Total Money {total_money}")
    update_user_data(database=data, user_id=user_id, field="money", data=total_money)
    update_user_data(database=data, user_id=user_id, field="last_join", data=current_time)
    print("Updated User Data")


def save_user_data(data, location):
    with open(location, "w") as f:
        json.dump(data, f, indent=5)
    print("saved")

async def setup(bot):
    await bot.add_cog(Currency(bot))
#Ensure that this is loaded into the discord bot

class Currency(commands.Cog, name="Currency"):
    def __init__(self, bot):
        self.bot = bot
        self.rate = 1
        self.data = load_user_data(location=USER_DATA)
        for user in self.data:
                update_user_data(database=self.data, user_id=user, field="last_join", data=time.time())

    async def increment_user_money(self, ctx, amnt):
        print("Try to increment")
        user_id = str(ctx.author.id)
        if user_id not in self.data:
            create_new_user(database=self.data, user_id=user_id)        #Check if the user exists or make a new user
        if ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.name != "waiting-room":
            print("In VC need to update money")
            update_money(data=self.data, rate=self.rate, current_time=time.time(), user_id=user_id)
        update_user_data(database=self.data, user_id=user_id, field="money", data=(self.data[user_id]['money']+amnt))
        save_user_data(self.data, USER_DATA)
        return self.data[user_id]['money']

    async def check_money(self,ctx):
        user_id = str(ctx.author.id)
        return self.data[user_id]['money']


    @commands.command(name='money', help=" - shows you how much money you currently have")
    async def money(self, ctx):
        print("money")
        user_id = str(ctx.author.id)
        if user_id not in self.data:
            create_new_user(database=self.data, user_id=user_id)        #Check if the user exists or make a new user
        if ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.name != "waiting-room":
            print("In VC")
            update_money(data=self.data, rate=self.rate, current_time=time.time(), user_id=user_id)
            await ctx.send(embed=discord.Embed(title="Current Balance",
                                               description=f"{ctx.author.mention}, you currently have ${self.data[user_id]['money']}",
                                               color=discord.Color.teal()))
        else:
            print("Not in VC")
            await ctx.send(embed=discord.Embed(title="Current Balance",
                                               description=f"{ctx.author}, you currently have ${self.data[user_id]['money']}",
                                               color=discord.Color.teal()))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        user_id = str(member.id)
        current_time = time.time()

        if before.channel is None and after.channel is not None:
            update_user_data(database=self.data, user_id=user_id, field="last_join", data=current_time)

        elif before.channel and before.channel.name == "waiting-room" and after.channel is not None:
            print(f"{member.name} moved from the waitingg room to {after.channel.name}")
            update_user_data(database=self.data, user_id=user_id, field="last_join", data=current_time)

        elif before.channel is not None and after.channel is None:
            update_money(data=self.data, rate=self.rate, current_time=time.time(),user_id=user_id)

        elif before.channel is not None and after.channel and after.channel.name == "waiting-room":
            update_money(data=self.data, rate=self.rate, current_time=time.time(), user_id=user_id)

        print(f"Before Channel {before.channel} After Channel {after.channel}")
        save_user_data(self.data, USER_DATA)
