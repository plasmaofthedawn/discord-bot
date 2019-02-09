import discord
import os
import asyncio
from random import randint

client = discord.Client()

mode = 0
player = None
voice = None

#runs when started
@client.event
async def on_ready():
    print("I'm in")
    print(client.user)

@client.event
async def on_message(message):
        
    if message.content == "/lt mode sitcom":
      mode = 1
    elif message.content == "/lt mode 0":
      mode = 0
    elif mode == 1 and message.author.name != "Laugh Track":
      await client.send_message(message.channel,'\*laugh track\*')
      if player.is_done():
        player = voice.create_ffmpeg_player(random_laugh())
        player.start()
    elif message.content == "/lt":
      await client.send_message(message.channel,'\*laugh track\*')
      if player.is_done():
        player = voice.create_ffmpeg_player(random_laugh())
        player.start()
    elif message.content == "/It":
      await client.send_message(message.channel, 'its lowercase l, not an uppercase i')

laughs = 5

def random_laugh():
   return 'laugh'+str(randint(1,laughs))+'.mp3'


client.run('')
