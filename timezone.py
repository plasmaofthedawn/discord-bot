import re

#dictionary of timezone abbreviations
timezone_abbreviations = {

}

#parses the timezone through inp,
def parse_timezone(inp):
    #search for "UTC" or "GMT" plus an additional but optional character and then numbers, and then an optional colon and more numbers
    ret = re.search(r'UTC[\D]?(?P<first>\d)+(?P<second>:\d+)?',inp)
    #if it it exists
    if ret:
        #if a second number exist
        if ret.group('second'):
            #add the first number to the second number/60
            return int(ret.group('first')) + int(ret.group('second')[1:])/60
        #otherwise
        elif ret.group('first'):
            #return the first number
            return int(ret.group('first'))
    #literally do the same thing but with GMT
    ret = re.search(r'GMT[\D]?(?P<first>\d)+(?P<second>:\d+)?',inp)
    # if it it exists
    if ret:
        # if a second number exist
        if ret.group('second'):
            # add the first number to the second number/60
            return int(ret.group('first')) + int(ret.group('second')[1:]) / 60
        # otherwise
        elif ret.group('first'):
            # return the first number
            return int(ret.group('first'))
    #search for it in our timezone_abrreviations dict
    try:
        #return the found value if found
        return timezone_abbreviations[inp]
    except KeyError:
        #otherwise, return false
        return False


if __name__ == "__main__":
    text = "UTC7:30"
    print(parse_timezone(text))

