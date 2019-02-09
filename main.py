import discord
import os
import asyncio
from random import randint

client = discord.Client()

mode = 0

#runs when started
@client.event
async def on_ready():
    print("I'm in")
    print(client.user)

#runs when a message was sent
@client.event
async def on_message(message):
    global mode
    
    #example message sorter
    if message.content == "/lt mode sitcom":
      #changes a global variable if this message
      mode = 1
    elif message.content == "/lt mode 0":
      #changes a global variable if this message
      mode = 0
    elif mode == 1 and message.author.name != "Laugh Track":
      #sends a message here
      await client.send_message(message.channel,'\*laugh track\*')
    elif message.content == "/lt":
      #sends a message here
      await client.send_message(message.channel,'\*laugh track\*')
    elif message.content == "/It":
      #sends a message here
      await client.send_message(message.channel, 'its lowercase l, not an uppercase i')


client.run('#discord-bot-token-replace')
