import discord
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

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
		

client.run('MTE2NzA3NjAxNzE3Nzg4Njc1MA.G5qDkR.aw_3tlMWqudjHbi4Q4WSMrzoaEZWM4nbDY7szQ')