import json
import discord
from texts import *
import database
import timezone
import io
from models import DAYS as days #*Days by FLOW starts playing*
from random import shuffle, randint
from random import shuffle, randint


startup = True
client = discord.Client()

with open('config.json', 'r') as read_file:
    config = json.load(read_file)

nouns = json.load(open("noun_ids.json", 'r'))

rounding_warning = ("Keep in mind that your schedule will be trimmed if " +
                    "it doesn't fit into increments of " + str(config["interval_block_size"]) +
                    " minute(s)")

abc = "abcdefghijklmnopqrstuvwxyz".upper()

pending_ballots = []
votingIndicator = "channel"
try:
    if(config["voting_channel"] == ""):
        votingIndicator = "trigger"
except KeyError:
    votingIndicator = "trigger"


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
        # get old timezone
        old_tz = database.get_user(message.author.id)
        if old_tz:
            old_intervals = old_tz.intervals
            old_tz = old_tz.timezone

        if params:
            try:
                tz = timezone.parse_timezone(params[0])
            except TypeError:
                tz = False
            if type(tz) != bool:# check if it's a bool:
                user = database.get_user(message.author.id)
                if not user:
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

            # if previous timezone existed
            if old_tz:
                # calculate change in time_zones
                tz_change = old_tz - tz
                # go through each interval
                for i in old_tz:
                    # remove the old interval
                    database.delete_interval(i.get_id())
                    # get new interval
                    new_interval = alter_timezone(i.start_day, i.start_hour, i.end_day, i.end_hour, tz_change)
                    # add the new interval
                    database.add_interval(message.author.id, new_interval[0], new_interval[2],
                                          new_interval[1], new_interval[3])
                await message.channel.send('updated all previous intervals')
                return
            else:
                await message.channel.send('%s is not a valid time zone.' % params[0])
                return
        else:
            await message.channel.send('set_time_zn requires one input, <timezone>.')

    @staticmethod
    async def add_interval(params, message):
        if(len(params) > 1):
            if("-" in params[1]):
                tmp = params[1].split("-", 1)
                params = [params[0], tmp[0], tmp[1]]
        if len(params) >= 3:
            if len(params) == 3:
                params = [params[0], params[1], params[0], params[2]]
            if(is_time(params[1]) and is_time(params[3])):
                times = [convert_time(params[1]), convert_time(params[3])]
            else:
                await message.channel.send("One of your times is not a time")
            tmp = [params[0], times[0], params[2], times[1]]
            tz = database.get_user(message.author.id)
            if(validInterval(tmp) != 1):
                await message.channel.send(validInterval(tmp))
                return
            if not tz:
                await message.channel.send("couldn't find your timezone in the database")
                return
            else:
                tz = tz.timezone

            try:
                start_day, start_hour, end_day, end_hour = alter_timezone(int(params[0]), times[0],
                                                                          int(params[2]), times[1], tz)
            except:
                await message.channel.send("Error processing interval")
                return

            database.add_interval(message.author.id, start_day, end_day, start_hour, end_hour)

            await message.channel.send("successfully created a new interval for %s." % message.author.name)

        else:
            await message.channel.send('\'add_interval\' requires 3-4 inputs, '
                                       '<start day> <start time> <end day>(if different) <end time>.' +
                                       " '0' being Sunday\n\n" + rounding_warning)

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
                await send(upload_schedule_help + "\n\n" + rounding_warning)
            elif params[0] == "example":
                await send(upload_schedule_example)
        else:
            if len(message.attachments) == 0:
                await send("Please attach the file with your message")
            else:
                user = database.get_user(message.author.id)
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

    @staticmethod
    async def export_csv(params, message):
        global days
        nick = 0 #whether or not to display nickname
        Id = 0 #whether or not to display user's discriminator
        i = 0
        while(i < len(params)):
            if(params[i] == "nick=1"):
                nick = 1
            elif(params[i] == "id=1"):
                Id = 1
            elif(params[i] == "help"):
                await message.channel.send(export_csv_help)
                raise TerminateFunction()
            i += 1
        if(nick and Id):
            await message.channel.send("Please choose either nick=1 or" +
            " id=1, not both.")
            return
        sep = ","
        raw = database.export_all_intervals()
        SBU = {} #sorted by user
        i = 0
        while(i < len(raw)):
            try:
                SBU[raw[i][1]]
            except KeyError:
                SBU[raw[i][1]] = []
            startD = raw[i][2]
            endD = raw[i][3]
            startT = raw[i][4] + (startD*24)
            endT = raw[i][5] + (endD*24)
            if(endT < startT):
                SBU[raw[i][1]].append((0, endT))
                endT = 7*24
            SBU[raw[i][1]].append((startT, endT))
            i += 1
        del raw
        users = list(SBU.keys())
        blockSize = config["interval_block_size"]#size of incrememnt blocks
        numOfBlocks = (7*24*60)/blockSize#number of blocks in a week
        blocksInDay = (24*60)/blockSize#number of blocks in a day
        i = 0
        while(i < len(users)):
            I = 0
            tmp = {} #list of each interval for each day
            while(I < 7):
                j = 0
                tmp[I] = {}
                while(j < blocksInDay):
                    tmp[I][j] = 0
                    j += 1
                I += 1
            I = 0
            tmp0 = SBU[users[i]] #list of intervals for current user
            while(I < len(tmp0)):
                j = 0
                while(j < numOfBlocks):
                    if(tmp0[I][0] <= ((blockSize*j)/60)):
                        if(tmp0[I][1] >= ((blockSize*(j+1))/60)):
                            day_ = ((blockSize*j)/60)//24
                            tmp[day_][j-(blocksInDay*day_)] = 1
                    j += 1
                I += 1
            SBU[users[i]] = tmp
            i += 1
        
        intervals = "" #time slots to be displayed at the top of the .csv file
        i = 0
        while(i < blocksInDay):
            intervals = (intervals + "," + to_time((i*blockSize)/60) + "-" +
            to_time(((i+1)*blockSize)/60))
            i += 1
        
        File = "" #string to be dumped into .csv file
        i = 0
        while(i < 7): #adding each user's intervals to a csv
            File = File + "\n\n" + days[i] + intervals + "\n\n"
            #intervals begins with a comma, if you were wondering why I dind't
            #   add one
            I = 0
            while(I < len(users)):
                j = 0
                user = await client.get_user_info(users[I])
                if(user != None):
                    if(nick):
                        name = user.display_name
                    elif(Id):
                        name = user.name + "#" + user.discriminator
                    else:
                        name = user.name
                    File = File + name + ","
                    while(j < blocksInDay):
                        File = File + str(SBU[users[I]][i][j]) + ","
                        j += 1
                    File = File[:-1] + "\n"
                I += 1
            i += 1
        tmp = io.BytesIO(File[2:].encode("utf-8"))
        tmp1 = discord.File(tmp, filename="schedule.csv")
        await message.channel.send(file=tmp1)
        tmp.close()
        
    @staticmethod
    async def kill_me(paras, message):
        await message.channel.send('You\'re already dead, ' +
'and your next line is "Nani!?"')

    @staticmethod
    async def clear_schedule(prams, message):
        # get user
        user = database.get_user(message.author.id)
        # make sure the user exists
        if not user:
            await message.channel.send("couldn't find your timezone in the database")
            return
        # loop through each interval
        for i in user.intervals:
            # poof it out of existence
            database.delete_interval(i.get_id())
        # let the user know
        await message.channel.send("deleted all of %s's intervals" % message.author.name)


@client.event
async def on_message(message):
    # get params and run command
    channel = str(message.channel)
    inMainChannel = channel == config["channel"] #True if in main channel
    if (message.content.startswith(config['trigger'])) and inMainChannel:
        content = message.content.replace(config['trigger'], '', 1).split(' ')
        command = content[0]
        params = []
        if len(content) > 1:
            params = content[1:]

        try:
            await getattr(Commands, command)(params, message)
        except AttributeError:
            await message.channel.send("'" + command + "' is not a command" +
                                       ", use 'help' to get a list of commands")
    else:
        voting = 0
        content = message.content
        if(votingIndicator == "channel"):#in voting channel, and starts w/ trigger
            if(message.content.startswith(config["trigger"])):
                voting = channel == config["voting_channel"]
            content = content.replace(config['trigger'], '', 1).split(' ')
        elif(inMainChannel):#starts w/ voting_trigger and is in main channel
            voting = message.content.startswith(config["voting_trigger"])
            content = content.replace(config['voting_trigger'], '', 1).split(' ')
        command = content[0]
        params = []
        if len(content) > 1:
            params = content[1:]
        
        if(voting):
            if(hasattr(ballot_commands, command)):
                await getattr(ballot_commands, command)(params, message)
            else:
                await message.channel.send("'" + command + "' is not a voting " +
                "command, use 'help' to get a list of commands")


class ballot_commands:
    @staticmethod
    async def test(params, message):
        await message.channel.send("Welcome To The Polls!")
    
    @staticmethod
    async def upload_ballot(params, message): # Sorry about the long lines
        send = message.channel.send
        if len(params) > 0:
            if params[0] == "help":
                await send(upload_ballot_help)
            elif params[0] == "example":
                await send(upload_ballot_example)
            return
        else:
            if len(message.attachments) == 0:
                await send("Please attach the file with your message")
            else:
                attached = message.attachments[0]
                ballot = await attachment_to_bytes(attached)
                ballot = ballot.decode("utf-8").replace("\n\n", "\n").replace("\n\n", "\n")
        
        tmp = ballot.split("\n")
        try:
            if('"' in tmp[0]):
                title = tmp[0].replace('\\"', "\n").split('"')[1].replace("\n", '"')
            else:
                title = tmp[0]
            finished = 0
            prompts = []
            options = []
            prom = 1
            I = -1
            i = 1
            while((i < len(tmp)) & (not finished)):
                if(prom == 1): #if this line is a prompt
                    prompt = tmp[i].replace('\\"', "\n").split('"')[1].replace("\n", '"')
                    if("{" not in tmp[i][len(prompt):]):
                        await send("'{' missing, see 'upload_ballot help'")
                        return
                    options.append([])
                    prompts.append(prompt)
                    prom = 0
                    I += 1
                elif('"' in tmp[i]): #this is an option
                    options[I].append(tmp[i].replace('\\"', "\n").split('"')[1].replace("\n", '"'))
                elif("}" == tmp[i].replace(" ", '')):
                    prom = 1
                elif("write-in:" == tmp[i][:9].lower()):
                    options[I].append(int(tmp[i][9:].replace(" ", '')))
                else:
                    await send("An error occurred at '" + tmp[i] + "'")
                    return
                i += 1
        except:
            await send("An error occurred, please make sure you've properly " +
            "formated everything, see 'upload_ballot help'")
            return
        Options = ""
        i = 0
        while(i < len(options)):
            Options = Options + "\n    Prompt " + str(i) + ":" + list_to_str(options[i][:-1])
            Options = Options + " Write-In = " + str(bool(options[i][-1]))
            i += 1
        
        global pending_ballots
        loops = 0
        matches = 1
        while(matches > 0):
            loops += 1
            if(loops > 1000):
                await send("Overload of pending ballots, couldn't find an ID")
                return
            ID = randint(0, 999)
            matches = 0
            while(i < len(pending_ballots)):
                if(pending_ballots[i]["ID"] == ID):
                    matches = 1
                i += 1
        ID = str(ID)
        if(len(ID) == 1):
            ID = "00" + ID
        elif(len(ID) == 2):
            ID = "0" + ID
        
        await send("Title: " + title + "\nPrompts: " + list_to_str(prompts) +
        "\nOptions: " + Options + "\n\n Confirm this ballot with 'confirm_" +
        "ballot " + ID + "'")
        
        pending_ballots.append({"title": title, "prompts": list_to_str(prompts),
        "options": list_to_str(options), "ID": ID, "author": message.author.id})

    @staticmethod
    async def confirm_ballot(params, message):
        # adds ballot to database, after confirmation by user
        global nouns
        send = message.channel.send
        keys = list(nouns.keys())
        shuffle(keys)
        if(len(params) == 0):
            await send("'confirm_ballot' requires the ID of a ballot")
            return
        try:
            int(params[0])
            ID = params[0]
        except:
            await send("Input was not a number")
            return
        global pending_ballots
        found = 0
        i = 0
        while(i < len(pending_ballots)):
            if(pending_ballots[i]["ID"] == ID):
                pb = pending_ballots[i] #pending ballot
                found = 1
            i += 1
        
        if(not found):
            await send("Ballot #" + ID + " is not a pending ballot")
            return
        
        noun = ""
        Max = 0
        i = 0
        while(i < len(keys)):
            if(nouns[keys[i]] != ""):
                if(int(nouns[keys[i]]) > Max):
                    Max = int(nouns[keys[i]])
            if(noun == ""):
                if(nouns[keys[i]] == ""):
                    noun = keys[i]
            i += 1
        ID = str(Max)
        if(len(ID) == 1):
            ID = "00" + ID
        elif(len(ID) == 2):
            ID = "0" + ID
        
        prompts = str_to_list(pb["prompts"])
        options = str_to_list(pb["options"])
        votes = []
        print(prompts)
        i = 0
        while(i < len(prompts)):
            I = 0
            votes.append([])
            while(I < len(options[i])):
                votes[i].append(0)
                I += 1
            i += 1
        author = message.author.id
        if(author == pb["author"]):
            if(database.add_ballot(pb["title"], ID, noun, pb["author"],
            pb["prompts"], pb["options"], list_to_str(votes))
            ):
                await send("Ballot added to the database with ID '" + ID + "'" +
                " and Noun '" + noun + "'")
            else:
                await send("An error occurred while adding ballot to database")
        else:
            await send("Access Denied")
    
    @staticmethod
    async def vote(params, message):
        send = message.channel.send
        if(len(params) == 0):
            await send("'vote' requires 2 parameters, see 'help'")
            return


    @staticmethod
    async def get_ballot(params, message):
        send = message.channel.send
        if(len(params) == 0):
            await send("'get_ballot' requires either the ballot's ID or noun")
            return
        
        info = database.get_ballot(params[0])
        if(info == 0):
            await send("'" + params[0] + "' ballot couldn't be found")
            return
        info = info[0]
        author = await client.get_user_info(info[3])
        author = author.name + "#" + author.discriminator
        prompts = str_to_list(info[4])
        options = str_to_list(info[5])
        votes = str_to_list(info[6]) #note update votes each time someone votes
        if(len(params) > 1):
            try:
                layout = int(params[1])
            except:
                await send("Invalid layout option, '" + params[1] + "'")
                return
        else:
            layout = 0
        if(layout == 0):
            sep1 = "{"
            sep2 = "}    "
        elif(layout == 1):
            sep1 = "{"
            sep2 = "}\n"
        global abc
        tmp = ""
        i = 0
        while(i < len(prompts)):
            tmp = tmp + prompts[i] + sep1
            I = 0
            while((I+1) < len(options[i])): # since last 'option' is write-in
                tmp = tmp + abc[I] + ".'" + options[i][I] + "' " + str(votes[i][I]) + ",   "
                I += 1
            tmp = tmp[:-4] + sep2
            i += 1
        prompts_options = tmp
        
        status = "Closed"
        if(info[8]):
            status = "Open"
        
        await send("Title: " + info[0] + "\nID: " + info[1] + "\nNoun: " +
        info[2] + "\nCreator: " + author + "\nPrompts: " + prompts_options +
        "\nStatus: " + status)
    
    @staticmethod
    async def help(params, message):
        await message.channel.send(voting_help)



@client.event
async def on_ready():
    global startup
    if startup:
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')


to_bool = lambda i: str(bool(int(i))) # converts string to bool, Ex "0" to "False"


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


def validInterval(interval):
    try:
        startD = int(interval[0])
        endD = int(interval [2])
    except TypeError:
        return "One of your days is not a number"
    startT = interval[1]
    endT = interval[3]
    if((startD < 0) or (startD > 6)):
        return "Invalid start day"
    elif((endD < 0) or (endD > 6)):
        return "Invalid end day"
    elif((startT >= 24) or (startT < 0)):
        return "Invalid start time"
    elif((endT >= 24) or (endT < 0)):
        return "Invalid end time"
    elif(((endT < startT) and (endD == startD)) or (endD < startD)):
        return ("I don't care how clocks work where you're from, here in " +
        "America clocks go forward!")
    elif((endT == startT) and (endD == startD)):
        return "Your end and start times are the same"
    else:
        return True


def convert_time(time_):
    # output time as a double, with optional offset
    is_t = 1
    time = time_
    if ":" not in time_:
        if ((time_[-2:] == "pm") or (time_[-2:] == "am")) and (len(time_) > 2):
            time = time[:-2] + ":00" + time[-2:]
        else:
            time = time + ":00"
    try:
        if time[-2:] == "pm":
            time = time[:-2]
            time = str(int(time[:-3]) + 12) + time[-3:]
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
        return int(time[:-3]) + (int(time[-2:]) / 60)
    else:
        return None


def is_time(time):
    return convert_time(time) is not None

def to_time(Float):
    #converts a float to a time (Ex: 1.25 to 1:15)
    mins = (Float-int(Float))*60
    if(mins > 0):
        return str(int(Float)) + ":" + mins
    else:
        return str(int(Float))

def process(schedule, user):
    days = ["sun", "mon", "tues", "wed", "thurs", "fri", "sat", "sunday",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    tmp = schedule.replace("\n\n", "\n").replace("\n\n", "\n")
    blocks = tmp.replace(" ", "").lower().split("}\n")
    blocks[-1] = blocks[-1].replace("\n}", "")
    i = 0
    entries = [[]]
    while(i < len(blocks)):
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
                return 0
        else:
            while j < 14:
                if blocks[i].split("{")[0] == days[j]:
                    day = j
                j += 1
            if day == -1:
                i = len(blocks)
                return 0
            elif day > 6:
                j -= 7
        try:
            lines = blocks[i].split("\n")[1:]
        except:
            return 0
        entries.append([])
        j = 0
        next_day = 0
        while (j < len(lines)) and ("-" in lines[j]):
            if "--" in lines[j]:
                lines[j] = lines[j].replace("--", "-")
                next_day = 1
            start, end = lines[j].split("-")
            if not is_time(start):
                return 0
            if not is_time(end):
                return 0
            if(is_time(start) and is_time(end)):
                start = convert_time(start)
                end = convert_time(end)
                if(start <= end):
                    return 0
            else:
                return 0
            entries[i].append((start, end, next_day, day, day_start, day_end))
            next_day = 0
            j += 1
        i += 1
    i = 0
    while i < len(blocks):
        j = 0
        if 1:
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
    return 1


async def attachment_to_bytes(attachment):
    tmp = io.BytesIO(b"")
    await attachment.save(tmp)
    ret = tmp.read()
    tmp.close()
    return ret


list_to_str = lambda List: json.dumps(List)
str_to_list = lambda Str: json.loads(Str)


if __name__ == "__main__":
    client.run(config['token'])
