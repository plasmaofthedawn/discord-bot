import json
import discord
import asyncio

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

client.run(config['token'])
