import discord
import typing
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import asyncio


async def setup(client):
    await client.add_cog(Music(client))

#
class Song():
    def __init__(self, user, url):
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.user = user
        if "youtube.com/" in url:
            print("Found Youtube.com")
            self.link = url
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            self.URL = info['formats'][0]['url']
            self.title = info.get('title', None)
        else:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
                self.link = info.get('webpage_url', None)
                self.URL = info['formats'][0]['url']
                self.title = info.get('title', None)



class Music(commands.Cog, name="Music"):
    def __init__(self, client):
        self.client = client
        self.Queue = []
        self.Loop = False

    @commands.command()
    async def hello(self, ctx):
        response = 'Hello!'
        await ctx.send(response)

    @commands.command(name='leave')
    async def leave(self, ctx):
        if ctx.voice_client:  # If the bot is in a voice channel
            ctx.voice_client.stop()
            self.Queue = []
            await ctx.guild.voice_client.disconnect()  # Leave the channel
            await ctx.send('Bot left')

    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.voice_client:
            voice = ctx.voice_client
            voice.stop()

    @commands.command(name='loop')
    async def loop(self, ctx):
        self.Loop = not self.Loop
        if self.Loop:
            await ctx.send("Looping is now Enabled")
        else:
            await ctx.send("Looping is now Disabled")


    @commands.command(name='remove')
    async def remove(self, ctx, number):
        number = int(number)
        if number-1 <len(self.Queue):
            Song = self.Queue[number-1]
            embed = discord.Embed(title=f"Removed {number} from Queue", description=f"[{Song.title}]({Song.link})",
                                  color=discord.Color.teal())
            await ctx.send(embed=embed)
            del self.Queue[number-1]
        else:
            await ctx.send("Enter a valid number")

    @commands.command(name='queue')
    async def queue(self, ctx, page: typing.Optional[int] = 1):
        print("In Queue")
        start = 10*(page-1)
        song_list = ""
        PageBuffer = self.Queue[start:(start+9)]
        print(PageBuffer)
        for i, song in enumerate(PageBuffer):
            song_list += ("[" + str(start+i+1) + " - "+ str(song.title) +f"]({song.link})" "\n")
        embed = discord.Embed(title=f"Queue", description=song_list,
                          color=discord.Color.teal())
        print("Should Send")
        await ctx.send(embed=embed)

    @commands.command(name='play')
    async def play(self, ctx, *, song):
        if ctx.author.voice:    # Check if user is in a VC
            if not ctx.voice_client:    # If the bot isnt in the VC Join It
                channel = ctx.message.author.voice.channel
                await channel.connect()
            voice = ctx.voice_client
            NewSong = Song(ctx.message.author.name, song)
            if voice.is_playing():
                await ctx.send(embed=discord.Embed(title="Added New Song to Queue",
                                                   description=f"[{NewSong.title}]({NewSong.link})" +
                                                               "\n\n In position #" +str(len(self.Queue)+1),
                                                   color=discord.Color.teal()))
            self.Queue.append(NewSong)
            play_next(self, ctx)

def play_next(self, ctx):
    if ctx.voice_client:
        voice = ctx.voice_client
        if len(self.Queue) > 0 and not voice.is_playing():
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}
            Song = self.Queue.pop(0)
            voice.play(FFmpegPCMAudio(Song.URL, **FFMPEG_OPTIONS, executable="C:/ffmpeg/bin/ffmpeg.exe"),
                             after=lambda e: play_next(self, ctx))
            voice.is_playing()
            embed = discord.Embed(title="Now Playing", description=f"[{Song.title}]({Song.link}) "
                                                                   f"\n\n Requested By: {Song.user}",
                                  color=discord.Color.teal())
            if self.Loop:
                self.Queue.append(Song)
            asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), self.client.loop)
    else:
        asyncio.run_coroutine_threadsafe(ctx.send("Please Join a Voice Channel"), self.client.loop)
        self.Queue = []
