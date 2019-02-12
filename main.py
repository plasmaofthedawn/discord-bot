import json
import discord
import asyncio
from texts import *

startup = True
client = discord.Client()

with open('config.json', 'r') as read_file:
    global config
    config = json.load(read_file)


# add each command as a static method to this class
class commands:
    @staticmethod
    async def test(params, message):
        if params:
            await message.channel.send('hello, {}!'.format(params[1]))
        else:
            await message.channel.send('hello, world!')
    @staticmethod
    async def help(params, message):
        await message.channel.send(help_txt)

@client.event
async def on_message(message):
    # get params and run command
    if message.content.startswith(config['trigger']):
        content = message.content.replace(config['trigger'], '', 1).split(' ')
        command = content[0]
        params = []
        if len(content) > 1:
            params = content[1:]

        await getattr(commands, command)(params, message)


@client.event
async def on_ready():
    global startup
    if startup:
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

def alter_timezone(start_day, start_hour, end_day, end_hour, timezone):

    start_hour -= timezone
    end_hour -= timezone

    if start_hour < 0:
        start_hour += 24
        start_day -= 1
        if start_day < 0:
            start_day += 7
    if end_hour  <0:
        end_hour += 24
        end_day -= 1
        if end_day < 0:
            end_day += 7

    return start_day, start_hour, end_day, end_hour

        
client.run(config['token'])
