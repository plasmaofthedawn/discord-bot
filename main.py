import json
import discord
from texts import *
import database
import timezone
import io

startup = True
client = discord.Client()

with open('config.json', 'r') as read_file:
    config = json.load(read_file)

# storage for loaded intervals
loaded_intervals = []
owner = 0


# add each command as a static method to this class
class Commands:
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
                if user == 0:
                    database.add_user(message.author.id, tz)
                    if tz > 0:
                        await message.channel.send(
                            '%s has been added to the database to with timezone UTC+%d.' % (message.author.name, tz))
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
                params = [params[0], params[1], params[0], params[2]]

            tz = database.get_user(message.author.id)
            if not tz:
                await message.channel.send("couldn't find your timezone in the database")
                return
            else:
                tz = tz.timezone

            try:
                start_day, start_hour, end_day, end_hour = alter_timezone(int(params[0]), int(params[1]),
                                                                          int(params[2]), int(params[3]), tz)
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
        global loaded_intervals
        global owner

        owner = 0
        loaded_intervals = []

        user = database.get_user(message.author.id)
        if not user or user.intervals == []:
            await message.channel.send('No intervals found for %s.' % message.author.name)
            return
        else:
            await message.channel.send("%s's timezone is UTC%d" % (message.author.name, user.timezone))
            await message.channel.send("Intervals (UTC adjusted):")
            text = ""
            iterator = 0
            owner = user.discord_id
            for i in user.intervals:
                text += "%d: %s\n" % (iterator, str(i))
                loaded_intervals.append(i.get_id())
                iterator += 1
            await message.channel.send(text)
            await message.channel.send("Use the left most number to delete the interval with !remove_interval")
            print(loaded_intervals)

    @staticmethod
    async def remove_interval(params, message):
        if params:
            try:
                params = int(params[0])
            except ValueError:
                await message.channel.send("The first argument should be a number.")
            if message.author.id == owner:
                try:
                    if database.delete_interval(loaded_intervals[params]):
                        await message.channel.send("Successfully deleted the interval with id %d" % params)
                        return
                    else:
                        await message.channel.send("Something went wrong.")
                        return
                except IndexError:
                    await message.channel.send("Too high of an index number.")
            else:
                await message.channel.send("Only the owner of the intervals can delete them.")
                await message.channel.send("If you were trying to delete your own intervals run !show_schedule first.")
                return
        else:
            await message.channel.send("Missing parameters.")
            return
    
    @staticmethod
    async def upload_schedule(params, message):
        send = message.channel.send
        if len(params) > 0:
            if params[0] == "help":
                await send(upload_schedule_help)
            elif params[0] == "example":
                await send(upload_schedule_example)
        else:
            if len(message.attachments) == 0:
                await send("Please attach the file with your message")
            else:
                user = database.get_user(message.author.id)
                print(user)
                if user != 0:
                    attached = message.attachments[0]
                    schedule = await attachment_to_bytes(attached)
                    if process(schedule.decode("utf-8"), user) == 0:
                        await send("Failed to process schedule, please " +
                                   "check that the formatting is correct, see " +
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
            await getattr(Commands, command)(params, message)
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


def alter_timezone(start_day, start_hour, end_day, end_hour, tz):
    start_hour -= tz
    end_hour -= tz
    
    if start_hour < 0:
        start_hour += 24
        start_day -= 1
        if start_day < 0:
            start_day += 7
    elif start_hour >= 25:
        start_hour -= 24
        start_day += 1
        if start_day > 6:
            start_day -= 7
    if end_hour < 0:
        end_hour += 24
        end_day -= 1
        if end_day < 0:
            end_day += 7
    elif end_hour >= 25:
        end_hour -= 24
        end_day += 1
        if end_day > 6:
            end_day -= 7
    return start_day, start_hour, end_day, end_hour


def convert_time(time_):
    # output time as a double
    is_t = 1
    time = time_
    if ":" not in time_:
        if ((time_[-2:] == "pm") or (time_[-2:] == "am")) and (len(time_) > 2):
            time = time[:-2] + ":00" + time[-2:]
        else:
            time = time + ":00"
        print("ping")
    try:
        if time[-2:] == "pm":
            time = time[:-2]
            time = str(int(time[:-3])+12) + time[-3:]
        elif time[-2:] == "am":
            time = time[:-2]
            if int(time[:-3]) > 12:
                is_t = 0
        
        if time[-3] != ":":
            is_t = 0
        elif (int(time[:-3]) < 0) or (int(time[:-3]) > 24):
            is_t = 0
        elif (int(time[-2:]) > 59) or (int(time[-2]) < 0):
            is_t = 0
    except ValueError:
        is_t = 0
    if is_t == 1:
        return int(time[:-3])+(int(time[-2:])/60)
    else:
        return None


def is_time(time):
    return convert_time(time) != None


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
    while (i < len(blocks)) and (not failed):
        j = 0
        day = -1
        day_start = -1
        day_end = -1
        if "-" in blocks[i].split("{")[0]:
            while j < 14:
                if blocks[i].split("{")[0].split("-")[0] == days[j]:
                    day_start = j
                j += 1
            if day_start > 6:
                day_start -= 7
            j = 0
            while j < 14:
                if blocks[i].split("{")[0].split("-")[1] == days[j]:
                    day_end = j
                j += 1
            if day_end > 6:
                day_end -= 7
            if (day_start == -1) or (day_end == -1):
                print("upload_schedule processing failure at " + blocks[i])
                failed = 1
        else:
            while j < 14:
                if blocks[i].split("{")[0] == days[j]:
                    day = j
                j += 1
            if day == -1:
                print("upload_schedule processing failure at " + blocks[i])
                i = len(blocks)
                failed = 1
            elif day > 6:
                j -= 7
        lines = blocks[i].split("\n")[1:]
        entries.append([])
        j = 0
        next_day = 0
        while (j < len(lines)) and ("-" in lines[j]) and (not failed):
            if "--" in lines[j]:
                lines[j] = lines[j].replace("--", "-")
                next_day = 1
            start, end = lines[j].split("-")
            if not is_time(start):
                print(start + " is not a time")
                failed = 1
            if not is_time(end):
                print(end + " is not a time")
                failed = 1
            start = convert_time(start)
            end = convert_time(end)
            entries[i].append((start, end, next_day, day, day_start, day_end))
            next_day = 0
            j += 1
        i += 1
    i = 0
    while (i < len(blocks)) and (not failed):
        j = 0
        if not failed:
            tz = user.timezone
            while j < len(entries[i]):
                day = entries[i][j][3]
                day_start = entries[i][j][4]
                day_end = entries[i][j][5]
                if day != -1:
                    if entries[i][j][2] == 1:
                        day_two = day + 1
                        if day == 6:
                            day_two = 0
                    else:
                        day_two = day
                    tmp = alter_timezone(day, entries[i][j][0], day_two, entries[i][j][1], tz)
                    print((day, entries[i][j][0], day_two, entries[i][j][1], tz))
                    print("toup")
                    database.add_interval(user.discord_id, tmp[0], tmp[2], tmp[1], tmp[3])
                else:
                    # day_start, day_end
                    day = day_start
                    running = 1
                    while running:
                        tmp = alter_timezone(day, entries[i][j][0], day, entries[i][j][1], tz)
                        database.add_interval(user.discord_id, tmp[0], tmp[2], tmp[1], tmp[3])
                        
                        if day == day_end:
                            running = 0
                        day += 1
                        if day > 6:
                            day = 0
                j += 1
        i += 1
    if failed:
        return 0
    else:
        return 1


async def attachment_to_bytes(attachment):
    tmp = io.BytesIO(b"")
    await attachment.save(tmp)
    return tmp.read()
    tmp.close()


client.run(config['token'])
