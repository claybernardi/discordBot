import discord
import Song
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio
import logging

async def setup(client):
    await client.add_cog(Music(client))


class Music(commands.Cog, name="Music"):
    def __init__(self, client):
        self.client = client
        self.Queue = []
        self.Loop = False
        self.currentSong = None
        self.autoLeave = True
        self.leaveTimer = 600
        self.volume = 1

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.client.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time >= self.leaveTimer:
                    voice.play(discord.FFmpegPCMAudio('C:/Users/Clayton/PycharmProjects/discordBot/goobnight.mp3', executable="C:/ffmpeg/bin/ffmpeg.exe")) #Add with mp3 file name
                    await asyncio.sleep(2)
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    @commands.command(name='autoleave', help=" - Toggles the bot auto-leave with inactivity feature")
    async def autoleave(self, ctx):
        self.autoLeave = not self.autoLeave
        if self.autoLeave:
            await ctx.send("Auto leaving is now Enabled")
        else:
            await ctx.send("Auto leaving is now Disabled")

    @commands.command(name='leavetimer', help=" - Sets the auto-leave timer (seconds)")
    async def leavetimer(self, ctx, seconds):
        if seconds is not None:
            seconds = int(seconds)
            if seconds > 3600:
                seconds = 3600
                await ctx.send("The max ammount of time is 3600 seconds or 1 hour, your input has been updated to 3600")
            self.leaveTimer = seconds
            await ctx.send(f"Leave timer updated to {seconds} seconds")
        else:
            await ctx.send("Please input a number of seconds to leave after")


    @commands.command(name='leave', description="Makes bot leave the voice channel", help=" - Makes bot leave the voice channel")
    async def leave(self, ctx):
        if ctx.voice_client:  # If the bot is in a voice channel
            ctx.voice_client.stop()
            voice = ctx.voice_client
            self.Queue = []
            voice.play(discord.FFmpegPCMAudio('C:/Users/Clayton/PycharmProjects/discordBot/goobnight.mp3',
                                              executable="C:/ffmpeg/bin/ffmpeg.exe"))  # Add with mp3 file name
            await asyncio.sleep(2)
            await ctx.guild.voice_client.disconnect()  # Leave the channel
        else:
            await ctx.send("I am not currently in a channel")

    @commands.command(name='skip', description="Skips whatever is currently being played", help=" - Skips to the next song")
    async def skip(self, ctx):
        if ctx.voice_client:
            voice = ctx.voice_client
            voice.stop()
        else:
            await ctx.send("I am not currently in a channel")

    @commands.command(name='skipto', description="Skips whatever is currently being played", help=" - Skips to the song number given")
    async def skipto(self, ctx, number):
        number = int(number)
        if self.Queue != []:
            if (number-1) <= len(self.Queue):
                if ctx.voice_client:
                    voice = ctx.voice_client
                    self.Queue = self.Queue[(number - 1):]
                    voice.stop()
                else:
                    await ctx.send("I am not currently in a channel")
            else:
                await ctx.send("The Queue is not that long")
        else:
            await ctx.send("I do not have anything in the Queue")


    @commands.command(name='stop', description="Stops the bot from playing and clears the Queue", help=" - Clears the queue and stops the player")
    async def stop(self, ctx):
        if ctx.voice_client:
            voice = ctx.voice_client
            self.Queue = []
            voice.stop()
        else:
            await ctx.send("I am not currently in a channel")

    @commands.command(name='pause', description="Pauses whatever is currently being played", help=" - Pauses the current song")
    async def pause(self, ctx):
        if ctx.voice_client:
            voice = ctx.voice_client
            if voice.is_playing():
                voice.pause()
            else:
                await ctx.send("I am not currently playing anything")
        else:
            await ctx.send("I am not currently in a channel")

    @commands.command(name='resume', description="Resumes whatever was being played when the bot was paused", help=" - Unpauses the song")
    async def resume(self, ctx):
        if ctx.voice_client:
            voice = ctx.voice_client
            if not voice.is_playing():
                voice.resume()
            else:
                await ctx.send("I am currently playing something")
        else:
            await ctx.send("I am not currently in a channel")

    @commands.command(name='loop', description="Toggles looping of the current Queue starting after the current song", help=" Loops the songs currently in the queue")
    async def loop(self, ctx):
        self.Loop = not self.Loop
        if self.Loop:
            if self.currentSong != None:
                self.Queue.append(self.currentSong)
            await ctx.send("Looping is now Enabled")
        else:
            await ctx.send("Looping is now Disabled")


    @commands.command(name='remove', help=" - Removes a specific track from the queue")
    async def remove(self, ctx, number: str = commands.parameter(description=" - The Position of the track to be removed")):
        number = int(number)
        if number-1 <len(self.Queue):
            Song = self.Queue[number-1]
            embed = discord.Embed(title=f"Removed {number} from Queue", description=f"[{Song.title}]({Song.link})",
                                  color=discord.Color.teal())
            await ctx.send(embed=embed)
            del self.Queue[number-1]
        else:
            await ctx.send("Enter a valid number")

    @commands.command(name='poop', help=" - Poops the queue")
    async def poop(self, ctx):
        for song in range(len(self.Queue)):
            del self.Queue[0]



    @commands.command(name='queue', description="Gives a list of the current tracks in the queue", help=" - Lists current queue")
    async def queue(self, ctx, page: str = commands.parameter(default=1,
                                                                description="The Position of the track to be removed")):
        page = int(page)
        start = 10*(page-1)
        song_list = ""
        PageBuffer = self.Queue[start:(start+9)]
        for i, song in enumerate(PageBuffer):
            song_list += ("[" + str(start+i+1) + " - "+ str(song.title) +f"]({song.link})" "\n")
        embed = discord.Embed(title=f"Queue", description=song_list,
                          color=discord.Color.teal())
        await ctx.send(embed=embed)

    # Add LoopThis, which loops a single song

    # Add a Shuffle or Looped Shuffle
    @commands.command(name='playing', description="Used to play or add something to the queue", help=" - Displays info on current song")
    async def playing(self, ctx):
        embed = discord.Embed(title="Now Playing", description=f"[{self.currentSong.title}]({self.currentSong.link}) "
                                                               f"\n\n Requested By: {self.currentSong.user} \n"
                                                               f"Song Length: {self.currentSong.duration_string()}",
                              color=discord.Color.teal())
        await ctx.send(embed=embed)

    @commands.command(name='volume', description='Used to change the volume of the bot')
    async def volume(self,ctx, volumeIn: int = commands.parameter(default=1,description="Desired Volume")):
        if (volumeIn>100):
            volumeIn=100
        elif (volumeIn<0):
            volumeIn = 0
        volumeIn = float(volumeIn/100)
        if ctx.voice_client:
            voice = ctx.voice_client
            voice.source = discord.PCMVolumeTransformer(voice.source, volume=(volumeIn/self.volume))
        self.volume = volumeIn
        embed = discord.Embed(title=f"Volume set to {self.volume * 100}%",
                              color=discord.Color.teal())
        await ctx.send(embed=embed)

    @commands.command(name='play', description="Used to play or add something to the queue")
    async def play(self, ctx, *, song: str = commands.parameter(description="A youtube link or what to search for")):
        logging.info("In play Command")
        if ctx.author.voice:    # Check if user is in a VC
            if not ctx.voice_client:    # If the bot isnt in the VC Join It
                channel = ctx.message.author.voice.channel
                logging.info("Waiting on connection")
                await channel.connect()
                logging.info("Connection Complete")
                voice = ctx.voice_client
                logging.info("Joined Channel")
            elif ctx.voice_client.channel != ctx.author.voice.channel:
                if self.Queue == [] and not ctx.voice_client.is_playing():
                    await ctx.guild.voice_client.disconnect()
                    channel = ctx.message.author.voice.channel
                    await channel.connect()
                    voice = ctx.voice_client
                else:
                    await ctx.send("The bot is currently being used in a different channel")
                    return
            else:
                voice = ctx.voice_client
            try:
                NewSong = Song.Song(ctx.message.author.name, song, ctx.message.author.id)
                logging.info("Added new song to queue")
                if voice.is_playing():
                    await ctx.send(embed=discord.Embed(title="Added New Song to Queue",
                                                       description=f"[{NewSong.title}]({NewSong.link})" +
                                                                   "\n\n In position #" + str(len(self.Queue) + 1) +
                                                       f"\nSong Length: {NewSong.duration_string()}",
                                                       color=discord.Color.teal()))
                self.Queue.append(NewSong)
                logging.info("Going to Play next")
                await Music.play_next(self, ctx)
            except TypeError:
                await ctx.send(embed=discord.Embed(title="Unable to add song to the queue - Unsupported Format",
                                                   color=discord.Color.red()))


    async def play_next(self, ctx):
        if ctx.voice_client:
            voice = ctx.voice_client
            if len(self.Queue) > 0 and not voice.is_playing():
                logging.info("Going to Play")
                FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                  'options': '-vn'}
                Song = self.Queue.pop(0)
                self.currentSong = None
                self.currentSong = Song
                a = 0
                while not voice.is_playing():       #So we dont get weird failed to play once errors
                    a += 1
                    if a>10:
                        embed = discord.Embed(title=f"Error Playing [{Song.title}]({Song.link})",
                                              description=f"Requested By: {Song.user}",
                                              color=discord.Color.red())
                        break
                    print('test')
                    audiostream = FFmpegPCMAudio(Song.URL, **FFMPEG_OPTIONS, executable="C:/ffmpeg/bin/ffmpeg.exe")
                    voice.play(audiostream, after=lambda e: asyncio.run(Music.play_next(self, ctx)))
                    voice.source=discord.PCMVolumeTransformer(voice.source,volume=self.volume)

                if voice.is_playing():
                    embed = discord.Embed(title="Now Playing", description=f"[{Song.title}]({Song.link}) "
                                                                           f"\n\n Requested By: {Song.user} \n"
                                          f"Song Length: {Song.duration_string()}",
                                          color=discord.Color.teal())
                    if self.Loop:
                        self.Queue.append(Song)
                asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), self.client.loop)
        #else:
         #   asyncio.run_coroutine_threadsafe(ctx.send("Please Join a Voice Channel"), self.client.loop)
          #  self.Queue = []