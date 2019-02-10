import sqlite3
from models import *
from timezone import TIMEZONES, DAYS

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


def create_tables():
    cursor.execute("""CREATE TABLE users (
                            discord_id INTEGER PRIMARY KEY,
                            timezone   INTEGER
                    )""")

    cursor.execute("""CREATE TABLE intervals (
                            id         INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id    INTEGER,
                            day        INTEGER,
                            start_hour INTEGER,
                            end_hour   INTEGER,
                            FOREIGN KEY(user_id) REFERENCES users(discord_id)
                    )""")


def add_user(discord_id, timezone):
    try:
        cursor.execute('INSERT INTO users  VALUES (?, ?)', (discord_id, timezone))
        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False


def add_interval(discord_id, day, start_hour, end_hour):
    try:
        cursor.execute('INSERT INTO intervals (user_id, day, start_hour, end_hour) VALUES (?, ?, ?, ?)',
                       (discord_id, day, start_hour, end_hour))
        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False


def get_user(discord_id):
    """
    :return: User (from models.py)
    """
    time_zone_id = cursor.execute("SELECT timezone from users WHERE discord_id = ?", (discord_id,)).fetchone()[0]
    db_intervals = cursor.execute("SELECT id, day, start_hour, end_hour FROM intervals WHERE user_id = ?",
                                  (discord_id,)).fetchall()

    # Map the enums to actual values
    time_zone = TIMEZONES[time_zone_id]
    intervals = [Interval(i[0], DAYS[i[1]], i[2], i[3]) for i in db_intervals]

    return User(discord_id, time_zone, intervals)


if __name__ == '__main__':
    remove_tables()
    create_tables()
    add_user(1, 2)
    add_interval(1, 2, 1, 5)
    add_interval(1, 3, 5, 21)
    print(get_user(1))

