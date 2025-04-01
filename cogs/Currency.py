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


def create_new_user(database, ctx):
    user_id = str(ctx.author.id)
    try:
        database[user_id] = {'name':ctx.author.name, "money": 100, "last_join": time.time()}
    except Exception as e:
        print(e)
    print(f"Created a new user for {ctx.author.name}")

def update_user_data(database, ctx, field, data, pass_user_id=None):
    try:
        user_id = str(ctx.author.id)
        database[user_id]['name'] = ctx.author.name
    except Exception:
        user_id = pass_user_id
    if user_id not in database:
        create_new_user(database=ctx, ctx=ctx)
    database[user_id][field] = data

def update_money(data, rate, ctx, current_time):
    user_id = str(ctx.author.id)
    try:
        money_earned = ((current_time - data[user_id]["last_join"]) / 60) * rate
    except Exception as e:
        print(e)
        data[user_id]["last_join"] = current_time
        money_earned = 0
    total_money = round(data[user_id]["money"] + money_earned, 2)
    update_user_data(database=data, ctx=ctx, field="money", data=total_money)
    update_user_data(database=data, ctx=ctx, field="last_join", data=current_time)


def save_user_data(data, location):
    with open(location, "w") as f:
        json.dump(data, f, indent=5)

async def setup(bot):
    await bot.add_cog(Currency(bot))
#Ensure that this is loaded into the discord bot

class Currency(commands.Cog, name="Currency"):
    def __init__(self, bot):
        self.bot = bot
        self.rate = 1
        self.data = load_user_data(location=USER_DATA)
        for user in self.data:
                update_user_data(database=self.data, pass_user_id=user, field="last_join", data=time.time(), ctx=None)

    async def increment_user_money(self, ctx, amnt):
        user_id = str(ctx.author.id)
        if user_id not in self.data:
            create_new_user(database=self.data, ctx=ctx)        #Check if the user exists or make a new user
        if ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.name != "waiting-room":
            update_money(data=self.data, rate=self.rate, current_time=time.time(), ctx=ctx)
        update_user_data(database=self.data, ctx=ctx, field="money", data=(self.data[user_id]['money']+amnt))
        save_user_data(self.data, USER_DATA)
        return self.data[user_id]['money']

    async def check_money(self,ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.data:
            create_new_user(database=self.data, ctx=ctx)
            save_user_data(self.data, USER_DATA)  # Check if the user exists or make a new user
        if ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.name != "waiting-room":
            update_money(data=self.data, rate=self.rate, current_time=time.time(), ctx=ctx)
            save_user_data(self.data, USER_DATA)
        return self.data[user_id]['money']


    @commands.command(name='money', help=" - shows you how much money you currently have")
    async def money(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.data:
            create_new_user(database=self.data, ctx=ctx)
            save_user_data(self.data, USER_DATA)#Check if the user exists or make a new user
        if ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.name != "waiting-room":
            update_money(data=self.data, rate=self.rate, current_time=time.time(), ctx=ctx)
            save_user_data(self.data, USER_DATA)
            await ctx.send(embed=discord.Embed(title="Current Balance",
                                               description=f"{ctx.author.mention}, you currently have ${self.data[user_id]['money']}",
                                               color=discord.Color.teal()))
        else:
            await ctx.send(embed=discord.Embed(title="Current Balance",
                                               description=f"{ctx.author}, you currently have ${self.data[user_id]['money']}",
                                               color=discord.Color.teal()))

    @commands.command(name='baltop', help=' - Shows who has the highest balance in the server')
    async def baltop(self, ctx):
        baltop_list = list(sorted(self.data.items(), key=lambda item: item[1]['money'], reverse=True))
        baltop_text = ''
        for index, (user_id, data) in enumerate(baltop_list[:5]):
            try:
                baltop_text += f"{index + 1}. {data['name']} - ${round(data['money'],2)}\n"
            except Exception as e:
                print(f"Exception is {e}")
        embed = discord.Embed(title="Top Server Balances", description=baltop_text, color=discord.Color.green())
        await ctx.send(embed=embed)



    @commands.Cog.listener()
    async def on_voice_state_update(self, ctx, before, after):
        user_id = str(ctx.author.id)
        current_time = time.time()

        if before.channel is None and after.channel is not None:
            update_user_data(database=self.data, ctx=ctx, field="last_join", data=current_time)

        elif before.channel and before.channel.name == "waiting-room" and after.channel is not None:
            print(f"{ctx.author.name} moved from the waitingg room to {after.channel.name}")
            update_user_data(database=self.data, ctx=ctx, field="last_join", data=current_time)

        elif before.channel is not None and after.channel is None:
            update_money(data=self.data, rate=self.rate, current_time=time.time(),ctx=ctx)

        elif before.channel is not None and after.channel and after.channel.name == "waiting-room":
            update_money(data=self.data, rate=self.rate, current_time=time.time(), ctx=ctx)

        print(f"Before Channel {before.channel} After Channel {after.channel}")
        save_user_data(self.data, USER_DATA)
