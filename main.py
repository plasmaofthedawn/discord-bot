import json
import discord
import asyncio
from texts import *
import database
import timezone
import io

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
    
    @staticmethod
    async def upload_schedule(params, message):
        send = message.channel.send
        if(len(params) > 0):
            if(params[0] == "help"):
                await send(upload_schedule_help)
            elif(params[0] == "example"):
                await send(upload_schedule_example)
        else:
            if(len(message.attachments) == 0):
                await send("Please attach the file with your message")
            else:
                user = database.get_user(message.author.id)
                print(user)
                if(user != 0):
                    attached = message.attachments[0]
                    schedule = await attachmentToBytes(attached)
                    if(process(schedule.decode("utf-8"), user) == 0):
                        await send("Failed to process schedule, please " +
                        "check that the formating is correct, see " +
                        "'!upload_schedule example' for an example")
                    else:
                        await send("No errors detected while processing schedule")
                else:
                    await send("Please set your time-zone before uploading")



@client.event
async def on_message(message):
    # get params and run command
    if message.content.startswith(config['trigger']):
        content = message.content.replace(config['trigger'], '', 1).split(' ')
        command = content[0]
        params = []
        if len(content) > 1:
            params = content[1:]
        
        try:
            await getattr(commands, command)(params, message)
        except AttributeError:
            await message.channel.send("'" + command + "' is not a command" +
            ", use '!help' to get a list of commands")
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
    elif(start_hour >= 25):
        start_hour -= 24
        start_day += 1
        if(start_day > 6):
            start_day -= 7
    if end_hour < 0:
        end_hour += 24
        end_day -= 1
        if end_day < 0:
            end_day += 7
    elif(end_hour >= 25):
        end_hour -= 24
        end_day += 1
        if(end_day > 6):
            end_day -= 7
    return start_day, start_hour, end_day, end_hour

def convTime(time_):
    #output time as a double, with optional offset
    is_Time = 1
    time = time_
    if(not ":" in time_):
        if(((time_[-2:] == "pm") or (time_[-2:] == "am")) and (len(time_) > 2)):
            time = time[:-2] + ":00" + time[-2:]
        else:
            time = time + ":00"
        print("ping")
    try:
        if(time[-2:] == "pm"):
            time = time[:-2]
            time = str(int(time[:-3])+12) + time[-3:]
        elif(time[-2:] == "am"):
            time = time[:-2]
            if(int(time[:-3]) > 12):
                is_Time = 0
        
        if(time[-3] != ":"):
            is_Time = 0
        elif((int(time[:-3]) < 0) or (int(time[:-3]) > 24)):
            is_Time = 0
        elif((int(time[-2:]) > 59) or (int(time[-2]) < 0)):
            is_Time = 0
    except ValueError:
        is_Time = 0
    if(is_Time == 1):
        return int(time[:-3])+(int(time[-2:])/60)
    else:
        return None

isTime = lambda time: (convTime(time) != None)

def process(schedule, user):
    days = ["sun", "mon", "tues", "wed", "thurs", "fri", "sat", "sunday", 
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    tmp = schedule.replace("\n\n", "\n").replace("\n\n", "\n")
    blocks = tmp.replace(" ", "").lower().split("}\n")
    blocks[-1] = blocks[-1].replace("\n}", "")
    print(blocks)
    i = 0
    failed = 0
    entries = [[]]
    while((i < len(blocks)) and (not failed)):
        I = 0
        day = -1
        dayStart = -1
        dayEnd = -1
        if("-" in blocks[i].split("{")[0]):
            while(I < 14):
                if(blocks[i].split("{")[0].split("-")[0] == days[I]):
                    dayStart = I
                I += 1
            if(dayStart > 6):
                dayStart -= 7
            I = 0
            while(I < 14):
                if(blocks[i].split("{")[0].split("-")[1] == days[I]):
                    dayEnd = I
                I += 1
            if(dayEnd > 6):
                dayEnd -= 7
            if((dayStart == -1) or (dayEnd == -1)):
                print("upload_schedule processing failure at " + blocks[i])
                failed = 1
        else:
            while(I < 14):
                if(blocks[i].split("{")[0] == days[I]):
                    day = I
                I += 1
            if(day == -1):
                print("upload_schedule processing failure at " + blocks[i])
                i = len(blocks)
                failed = 1
            elif(day > 6):
                I -= 7
        lines = blocks[i].split("\n")[1:]
        entries.append([])
        I = 0
        nextDay = 0
        while((I < len(lines)) and ("-" in lines[I]) and (not failed)):
            if("--" in lines[I]):
                lines[I] = lines[I].replace("--", "-")
                nextDay = 1
            start, end = lines[I].split("-")
            if(not isTime(start)):
                print(start + " is not a time")
                failed = 1
            if(not isTime(end)):
                print(end + " is not a time")
                failed = 1
            start = convTime(start)
            end = convTime(end)
            entries[i].append((start, end, nextDay, day, dayStart, dayEnd))
            nextDay = 0
            I += 1
        i += 1
    i = 0
    while((i < len(blocks)) and (not failed)):
        I = 0
        if(not failed):
            tz = user.timezone
            while(I < len(entries[i])):
                day = entries[i][I][3]
                dayStart = entries[i][I][4]
                dayEnd = entries[i][I][5]
                if(day != -1):
                    if(entries[i][I][2] == 1):
                        dayTwo = day + 1
                        if(day == 6):
                            dayTwo = 0
                    else:
                        dayTwo = day
                    tmp = alter_timezone(day, entries[i][I][0], dayTwo, entries[i][I][1], tz)
                    print((day, entries[i][I][0], dayTwo, entries[i][I][1], tz))
                    print("toup")
                    database.add_interval(user.discord_id, tmp[0], tmp[2], tmp[1], tmp[3])
                else:
                    #dayStart, dayEnd
                    day = dayStart
                    running = 1
                    while(running):
                        tmp = alter_timezone(day, entries[i][I][0], day, entries[i][I][1], tz)
                        database.add_interval(user.discord_id, tmp[0], tmp[2], tmp[1], tmp[3])
                        
                        if(day == dayEnd):
                            running = 0
                        day += 1
                        if(day > 6):
                            day = 0
                I += 1
        i += 1
    if(failed):
        return 0
    else:
        return 1


async def attachmentToBytes(attachment):
    tmp = io.BytesIO(b"")
    await attachment.save(tmp)
    return tmp.read()
    tmp.close()



client.run(config['token'])
