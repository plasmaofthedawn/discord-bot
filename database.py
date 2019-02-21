import sqlite3
from models import *
from json import load

config = load(open("config.json", 'r'))
db = sqlite3.connect('database.db')
cursor = db.cursor()


def remove_tables():
    try:
        cursor.execute('DROP TABLE intervals')
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        pass

    try:
        cursor.execute('DROP TABLE users')
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        pass
    
    try:
        cursor.execute("DROP TABLE ballots")
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        pass


def create_tables():
    cursor.execute("""CREATE TABLE users (
                            discord_id INTEGER PRIMARY KEY,
                            timezone   DOUBLE
                    )""")

    cursor.execute("""CREATE TABLE intervals (
                            id         INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id    INTEGER,
                            start_day  INTEGER,
                            end_day    INTEGER,
                            start_hour DOUBLE,
                            end_hour   DOUBLE,
                            FOREIGN KEY(user_id) REFERENCES users(discord_id)
                    )""")

    cursor.execute("""CREATE TABLE ballots (
                            title    TEXT,
                            id       TEXT,
                            noun     TEXT,
                            creator  TEXT,
                            prompts  TEXT,
                            options  TEXT,
                            votes    TEXT,
                            vote_log TEXT,
                            open     INTEGER
                    )""")#votes is the score for each option
#voting_log is a list of all of the messages, this is useful for double checking

def add_user(discord_id, timezone):
    try:
        cursor.execute('INSERT INTO users  VALUES (?, ?)', (discord_id, timezone))
        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False


def add_interval(discord_id, start_day, end_day, start_hour, end_hour):
    block_size = config["interval_block_size"]/60
    numOfBlocks = start_hour//block_size
    startHour = start_hour
    startDay = start_day
    if(start_hour > (numOfBlocks*block_size)):
        startHour = (numOfBlocks+1)*block_size
        if(startHour >= 24):
            startDay += 1
            startHour -= 24
            if(startDay > 6):
                startDay = 0
    numOfBlocks = end_hour//block_size
    endHour = numOfBlocks*block_size
    if((startHour != endHour) | (startDay != end_day)):
        try:
            cursor.execute('INSERT INTO intervals (user_id, start_day, end_day, start_hour, end_hour) '
                           'VALUES (?, ?, ?, ?, ?)', (discord_id, startDay, end_day, startHour, endHour))
            db.commit()

            return True

        except sqlite3.DatabaseError:
            return False



def get_user(discord_id):
    """
    :return: User (from models.py) or false if no user found
    """
    try:
        time_zone = cursor.execute("SELECT timezone from users WHERE discord_id = ?", (discord_id,)).fetchone()[0]
    except TypeError:
        # if no user is found then fetchone[0] would return None, which would cause a typeerror
        return False

    db_intervals = cursor.execute("SELECT id, start_day, end_day, start_hour, end_hour FROM "
                                  "intervals WHERE user_id = ?", (discord_id,)).fetchall()

    # put interval values into interval model
    intervals = [Interval(i[0], i[1], i[2], i[3], i[4]) for i in db_intervals]

    return User(discord_id, time_zone, intervals)


def update_user(discord_id, timezone):
    try:
        cursor.execute('UPDATE users SET timezone=? WHERE discord_id=?', (timezone, discord_id))

        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False


def delete_interval(interval_id):
    try:

        cursor.execute('DELETE FROM intervals WHERE id=?', (interval_id,))

        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False

def add_ballot(title, ID, noun, creator, prompts, options, votes):
    
    try:
        cursor.execute('INSERT INTO ballots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (title, ID, noun, creator, prompts, options, votes, "", 1))
        db.commit()
        return 1

    except sqlite3.DatabaseError:
        return 0


def get_ballot(inp):
    try: #if ID
        int(inp)
        tmp = cursor.execute("SELECT * FROM ballots WHERE id=?", (inp,)).fetchall()
    except ValueError: #if noun
        tmp = cursor.execute("SELECT * FROM ballots WHERE noun=?", (inp,)).fetchall()
    
    if(len(tmp) == 0):
        return 0
    else:
        return tmp


if __name__ == '__main__':
    remove_tables()
    create_tables()
    print(get_user(234387706463911939))
