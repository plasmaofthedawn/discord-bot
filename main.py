import discord
import os
import asyncio
from random import randint

client = discord.Client()

mode = 0
player = None
voice = None

@client.event
async def on_ready():
    global player
    global voice
    print("I'm in")
    print(client.user)
    for i in client.servers:
      for j in i.channels:
        if j.name == "laugh":
          channel = j
          break
      voice = await client.join_voice_channel(channel)
      player = voice.create_ffmpeg_player(random_laugh())
      player.start()

@client.event
async def on_message(message):
    global mode
    global player
    global voice
        
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


client.run('NDk0MjgzNDA3NjQ4MzU4NDMw.DoxTGA.HpHRyOI0-hNobeMGI4N1KD5lypE')