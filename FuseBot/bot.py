# discord imports
import discord
from discord.ext import commands

# other imports
import random
import asyncio
import os
import yt_dlp
import dotenv
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# GLOBAL VARIABLES

# for music
queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

# sleepy stuf
people_sleeping_cache = []
answers = ["yes", "no"]

# other
emojis = ["<:hello3:1326319373064994938>", "<:gato:1326319173009145949>", "<:catwithglasses:1326319138070597642>", "<:sillycat:1326319037688320054>"]


@bot.event
async def on_ready():
    print("FuseBot has logged on! ")

@bot.hybrid_command()
async def sync(ctx: commands.Context):
    await ctx.send("Syncing...")
    await bot.tree.sync()

@bot.hybrid_command()
async def ping(ctx: commands.Context):
    await ctx.send('pong')

@bot.hybrid_command()
async def skibidi(ctx: commands.Context):
    await ctx.send('toilet')

#region Music Playing

@bot.hybrid_command()
async def play(ctx: commands.Context, url):
    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client

    except Exception as e:
        print(e)
        
    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
        voice_clients[ctx.guild.id].play(player)
        #get video title
        
        info_dict = ytdl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        await ctx.channel.send("Playing " + "`" + video_title + "`")
        
    except Exception as e:
        print(e)

@bot.hybrid_command()
async def pause(ctx: commands.Context):
    try:
        voice_clients[ctx.guild.id].pause()
        await ctx.channel.send("Music Paused")
    except Exception as e:
        print(e)

@bot.hybrid_command()
async def resume(ctx: commands.Context):
    try:
        voice_clients[ctx.guild.id].resume()
        await ctx.channel.send("Music Resumed :D")
    except Exception as e:
        print(e)

@bot.hybrid_command()
async def stop(ctx: commands.Context):
    try:
        voice_clients[ctx.guild.id].stop()
        await ctx.channel.send("Music Stopped :<")
    except Exception as e:
        print(e)

@bot.hybrid_command()
async def join(ctx: commands.Context):
    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
        await ctx.channel.send("hello :D")
        await ctx.channel.send(emojis[0])
        await ctx.author.voice.channel.connect()
    except Exception as e:
        print(e)

@bot.hybrid_command()
async def leave(ctx: commands.Context):
    try:    
        await voice_clients[ctx.guild.id].disconnect()
        await ctx.channel.send("leaving vc, byebye")
    except Exception as e:
        print(e)
        
#endregion

@bot.event
async def on_message(message=discord.message.Message):
    if message.author == bot.user:
        return
    
    if message.content == "fusebot" or message.content == "Fusebot":
        await message.channel.send('hello im fusebot :D')
        await message.channel.send(emojis[0])

    if message.content.startswith('fusebot help'):
        await message.channel.send('hi im fusebot :D')
        await message.channel.send('command list:')
        await message.channel.send('music: ?join, ?play, ?pause, ?resume, ?stop, ?leave')
        await message.channel.send('other: "walter", "fusebot im sleeping", "cat"')
    
	#region sleepy stuff

    if message.content.startswith('fusebot im sleeping'):
        await message.channel.send('oka :D')
        userid = message.author.id
        people_sleeping_cache.append(userid)
        people_sleeping_cache.append(message.id)
	
    if (people_sleeping_cache.__contains__(message.author.id)):
        if(people_sleeping_cache.__contains__(message.id)):
            pass
        else:
            await message.channel.send('Welcome back :D')
            removalid = message.author.id
            i = people_sleeping_cache.index(removalid)
            people_sleeping_cache.pop(i + 1)
            people_sleeping_cache.remove(removalid)
	
    for i in range(len(people_sleeping_cache)):
        if(f"<@{people_sleeping_cache[i]}>" in message.content):
            await message.channel.send('That person is sleeping rn')
	
    if message.content.startswith('test'):
        await message.channel.send(people_sleeping_cache)
	
    #endregion

	# other random stuff
    
    if message.content.__contains__('walter'):
        await message.channel.send("https://tenor.com/view/walter-white-breaking-bad-meme-memes-funny-gif-23338269")
    
    if message.content.startswith('cat'):
        i = random.randint(0, len(emojis) - 1)
        await message.channel.send(emojis[i])

	#ping people
    if message.content.startswith('fusebot ping baka'):
        i = 0
        while i != 20:
            await message.channel.send(os.getenv("BAKA_ID"))
            i+= 1
	
    if message.content.startswith('fusebot ping ' + os.getenv("PERSON_NAME1")):
        await message.channel.send(os.getenv("PERSON_NAME1_ID") + os.getenv("MESSAGE_FOR_PERSON_NAME1"))

    if message.content.endswith('?'):
        value = random.randint(1, 1000)
        await message.channel.send(answers[value%2])	

bot.run(os.getenv("DISCORD_TOKEN"))