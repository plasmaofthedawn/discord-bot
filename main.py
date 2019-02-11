import json
import discord
import asyncio
import database
import timezone

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
    async def set_time_zn(params, message):
        if params:
            try:
                tz = timezone.parse_timezone(params[0])
            except TypeError:
                tz = False
            if tz:
                user = database.get_user(message.author.id)
                if user == False:
                    database.add_user(message.author.id, tz)
                    if tz > 0:
                        await message.channel.send(
                            '%s has been added to the database to with timezone UTC+%d.' % (message.author.name,tz))
                        return
                    else:
                        await message.channel.send(
                            '%s has been added to the database to with timezone UTC%d.' % (message.author.name, tz))
                        return
                else:
                    database.update_user(message.author.id, tz)
                    if tz > 0:
                        await message.channel.send(
                            'Timezone has been updated to UTC+%d for %s.' % (tz, message.author.name))
                        return
                    else:
                        await message.channel.send(
                            'Timezone has been updated to UTC%d for %s.' % (tz, message.author.name))
                        return
            else:
                await message.channel.send('%s is not a valid time zone.' % params[0])
                return
        else:
            await message.channel.send('set_time_zn requires one input, <timezone>.')

    @staticmethod
    async def add_interval(params, message):
        if len(params) >= 3:
            if len(params) == 3:
                params = [params[0],params[1],params[0],params[2]]

            tz = database.get_user(message.author.id)
            if not tz:
                await message.channel.send("couldn't find your timezone in the database")
                return
            else:
                tz = tz.timezone

            try:
                start_day, start_hour, end_day, end_hour = alter_timezone(int(params[0]),int(params[1]),
                                                                          int(params[2]),int(params[3]),tz)
            except TypeError:
                await message.channel.send("one of your inputs is not a number")
                return

            database.add_interval(message.author.id, start_day, end_day, start_hour, end_hour)

            await message.channel.send("successfully created a new interval for %s." % message.author.name)

        else:
            await message.channel.send('add_interval requires 3-4 inputs, '
                                       '<start day> <start time> <end day>(if different) <end time>.')

    @staticmethod
    async def show_schedule(params, message):
        await message.channel.send("Schedule for %s:" % message.author.name)
        await message.channel.send(database.get_user(message.author.id))


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
    if end_hour < 0:
        end_hour += 24
        end_day -= 1
        if end_day < 0:
            end_day += 7
    return start_day, start_hour, end_day, end_hour



client.run(config['token'])
