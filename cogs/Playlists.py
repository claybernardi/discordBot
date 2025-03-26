import discord
import Song
from discord.ext import commands

async def setup(client):
    await client.add_cog(Playlist(client))

class Playlist(commands.Cog, name="Playlist"):
    def __init__(self, client):
        self.client = client

#def createPlaylist(options):
    #Create a New Playlist
#def deleteFromPlaylist(options):
    #Make sure to delete playlist if it is empty
#def listPlaylist(options):
    #List all availible playlists
#def addToPlaylist(options):
    #Add a Song to a playlist

    #@commands.command(name='playlist', description="Command to Access all of the Playlist Features")
    async def playlist(self, ctx, cmd, *, options):
        cmd = cmd.lower()
        if cmd == 'create':
            if options == 'help':
                await ctx.send
            #createPlaylist(options)
        elif cmd == 'delete':
            if options == 'help':
                await ctx.send
            #deleteFromPlaylist(options)
        elif cmd == 'list':
            if options == 'help':
                await ctx.send
            #listPlaylist(options)
        elif cmd == 'add':
            if options == 'help':
                await ctx.send
            #addToPlaylist(options)