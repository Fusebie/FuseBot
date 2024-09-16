import discord
import random
import asyncio
import os
import requests
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
import utilities

load_dotenv()

# discord token
token = 'MTE2NzA3NjAxNzE3Nzg4Njc1MA.G5qDkR.aw_3tlMWqudjHbi4Q4WSMrzoaEZWM4nbDY7szQ'

# bot intents
intents = discord.Intents(messages=True, guilds=True, members=True, message_content=True, presences=True)
intents.message_content = True
intents.members = True

# command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# reconnect to yt server immediately upon being disconnected  
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

client = discord.Client(intents=intents)

# terminate sessions after sometime when idle
sessions = []


def check_session(ctx):
    """
    Checks if there is a session with the same characteristics (guild and channel) as ctx param.

    :param ctx: discord.ext.commands.Context

    :return: session()
    """
    if len(sessions) > 0:
        for i in sessions:
            if i.guild == ctx.guild and i.channel == ctx.author.voice.channel:
                return i
        session = utilities.Session(
            ctx.guild, ctx.author.voice.channel, id=len(sessions))
        sessions.append(session)
        return session
    else:
        session = utilities.Session(ctx.guild, ctx.author.voice.channel, id=0)
        sessions.append(session)
        return session

# music playing stuff

def prepare_continue_queue(ctx):
    """
    Used to call next song in queue.

    Because lambda functions cannot call async functions, I found this workaround in discord's api documentation
    to let me continue playing the queue when the current song ends.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    fut = asyncio.run_coroutine_threadsafe(continue_queue(ctx), bot.loop)
    try:
        fut.result()
    except Exception as e:
        print(e)


async def continue_queue(ctx):
    """
    Check if there is a next in queue then proceeds to play the next song in queue.

    As you can see, in this method we create a recursive loop using the prepare_continue_queue to make sure we pass
    through all songs in queue without any mistakes or interaction.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    session = check_session(ctx)
    if not session.q.theres_next():
        await ctx.send("queue finished")
        return

    session.q.next()

    voice = discord.utils.get(bot.voice_clients, guild=session.guild)
    source = await discord.FFmpegOpusAudio.from_probe(session.q.current_music.url, **FFMPEG_OPTIONS)

    if voice.is_playing():
        voice.stop()

    voice.play(source, after=lambda e: prepare_continue_queue(ctx))
    await ctx.send(session.q.current_music.thumb)
    await ctx.send(f"Now playing: {session.q.current_music.title}")


@bot.command(name='play')
async def play(ctx, *, arg):
    """
    Checks where the command's author is, searches for the music required, joins the same channel as the command's
    author and then plays the audio directly from YouTube.

    :param ctx: discord.ext.commands.Context
    :param arg: str
        arg can be url to video on YouTube or just as you would search it normally.
    :return: None
    """
    try:
        voice_channel = ctx.author.voice.channel

    # If command's author isn't connected, return.
    except AttributeError as e:
        print(e)
        await ctx.send("You're not connected to a voice channel")
        return

    # Finds author's session.
    session = check_session(ctx)

    # Searches for the video
    with youtube_dl.YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try:
            requests.get(arg)
        except Exception as e:
            print(e)
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)[
                'entries'][0]
        else:
            info = ydl.extract_info(arg, download=False)

    url = info['formats'][0]['url']
    thumb = info['thumbnails'][0]['url']
    title = info['title']

    session.q.enqueue(title, url, thumb)

    # Finds an available voice client for the bot.
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await voice_channel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # If it is already playing something, adds to the queue
    if voice.is_playing():
        await ctx.send(thumb)
        await ctx.send(f"Added to queue: {title}")
        return
    else:
        await ctx.send(thumb)
        await ctx.send(f"Now Playing: {title}")

        # Guarantees that the requested music is the current music.
        session.q.set_last_as_current()

        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        voice.play(source, after=lambda ee: prepare_continue_queue(ctx))


@bot.command(name='next', aliases=['skip'])
async def skip(ctx):
    """
    Skips the current song, playing the next one in queue if there is one.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    # Finds author's session.
    session = check_session(ctx)
    # If there isn't any song to be played next, return.
    if not session.q.theres_next():
        await ctx.send("nothing in the queue to play")
        return

    # Finds an available voice client for the bot.
    voice = discord.utils.get(bot.voice_clients, guild=session.guild)

    # If it is playing something, stops it. This works because of the "after" argument when calling voice.play as it is
    # a recursive loop and the current song is already going to play the next song when it stops.
    if voice.is_playing():
        voice.stop()
        return
    else:
        # If nothing is playing, finds the next song and starts playing it.
        session.q.next()
        source = await discord.FFmpegOpusAudio.from_probe(session.q.current_music.url, **FFMPEG_OPTIONS)
        voice.play(source, after=lambda e: prepare_continue_queue(ctx))
        return


@bot.command(name='print')
async def print_info(ctx):
    """
    A debug command to find session id, what is current playing and what is on the queue.
    :param ctx: discord.ext.commands.Context
    :return: None
    """
    session = check_session(ctx)
    await ctx.send(f"Session ID: {session.id}")
    await ctx.send(f"Música atual: {session.q.current_music.title}")
    queue = [q[0] for q in session.q.queue]
    await ctx.send(f"Queue: {queue}")


@bot.command(name='leave')
async def leave(ctx):
    """
    If bot is connected to a voice channel, it leaves it.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected:
        check_session(ctx).q.clear_queue()
        await voice.disconnect()
    else:
        await ctx.send("I'm not even in the vc")


@bot.command(name='pause')
async def pause(ctx):
    """
    If playing audio, pause it.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Music Paused")


@bot.command(name='resume')
async def resume(ctx):
    """
    If audio is paused, resumes playing it.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused:
        voice.resume()
    else:
        await ctx.send("already paused")


@bot.command(name='stop')
async def stop(ctx):
    """
    Stops playing audio and clears the session's queue.

    :param ctx: discord.ext.commands.Context
    :return: None
    """
    session = check_session(ctx)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing:
        voice.stop()
        session.q.clear_queue()
    else:
        await ctx.send("There's nothing playing")

# music playing stuff done

# GLOBAL VARIABLES
people_sleeping_cache = []
answers = ["yes", "no"]

@client.event
async def on_ready():
	print("FuseBot has logged on! ")

@client.event
async def on_message(message=discord.message.Message):
	if message.author == client.user:
		return
	if message.content.startswith('fusebot help'):
		await message.channel.send('hi im fusebot :D')
	
	# sleepy stuff

	if message.content.startswith('fusebot im sleeping'):
		await message.channel.send('oka :D')
		userid = message.author.id
		people_sleeping_cache.append(userid)
		people_sleeping_cache.append(message.id)
	
	if(people_sleeping_cache.__contains__(message.author.id)):
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
			await message.channel.send('That nigga is sleeping rn')
	
	if message.content.startswith('test'):
		await message.channel.send(people_sleeping_cache)
	
	# other random stuff

	if message.content.startswith('fusebot sex'):
		await message.channel.send('https://tenor.com/view/me-when-me-when-sex-funny-meme-gif-20625840')

	#ping baka

	if message.content.startswith('fusebot ping baka'):
		i = 0
		while i != 20:
			await message.channel.send('<@1134346518913093724> niggacat')
			i+= 1
	
	if message.content.endswith('?'):
		value = random.randint(1, 1000)
		await message.channel.send(answers[value%2])
		

client.run(token)