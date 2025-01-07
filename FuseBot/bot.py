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

queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

# GLOBAL VARIABLES
people_sleeping_cache = []
answers = ["yes", "no"]

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

@bot.event
async def on_message(message=discord.message.Message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('fusebot help'):
        await message.channel.send('hi im fusebot :D')
	
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

    #region music playing stuff

    if message.content.startswith("?play"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:
            url = message.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_clients[message.guild.id].play(player)

            #get video title
            
            info_dict = ytdl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)

            await message.channel.send("Playing " + "`" + video_title + "`")
            
        except Exception as e:
            print(e)

    if message.content.startswith("?pause"):
        try:
            voice_clients[message.guild.id].pause()
            await message.channel.send("Music Paused")
        except Exception as e:
            print(e)

    if message.content.startswith("?resume"):
        try:
            voice_clients[message.guild.id].resume()
            await message.channel.send("Music Resumed :D")
        except Exception as e:
            print(e)

    if message.content.startswith("?stop"):
        try:
            voice_clients[message.guild.id].stop()
            await message.channel.send("Music Stopped :<")
        except Exception as e:
            print(e)

    if message.content.startswith("?leave") or message.content.startswith("?disconnect"):
        await message.channel.send("leaving vc, byebye")
        await voice_clients[message.guild.id].disconnect()

    #endregion

	# other random stuff
    
	#ping baka

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