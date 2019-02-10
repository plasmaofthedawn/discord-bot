import sqlite3
from models import *

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


def add_user(discord_id, timezone):
    try:
        cursor.execute('INSERT INTO users  VALUES (?, ?)', (discord_id, timezone))
        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False


def add_interval(discord_id, start_day, end_day, start_hour, end_hour):
    try:
        cursor.execute('INSERT INTO intervals (user_id, start_day, end_day, start_hour, end_hour) VALUES (?, ?, ?, ?, ?)',
                       (discord_id, start_day, end_day, start_hour, end_hour))
        db.commit()

        return True

    except sqlite3.DatabaseError:
        return False



def get_user(discord_id):
    """
    :return: User (from models.py)
    """
    time_zone = cursor.execute("SELECT timezone from users WHERE discord_id = ?", (discord_id,)).fetchone()[0]
    db_intervals = cursor.execute("SELECT id, start_day, end_day, start_hour, end_hour FROM intervals WHERE user_id = ?",
                                  (discord_id,)).fetchall()

    # put interval values into interval model
    intervals = [Interval(i[0], i[1], i[2], i[3], i[4]) for i in db_intervals]

    return User(discord_id, time_zone, intervals)


if __name__ == '__main__':
    remove_tables()
    create_tables()
    add_user(1, 2)
    add_interval(1, 1, 1, 1.75, 5.5)
    add_interval(1, 1, 1, 6.0, 21.0)
    print(get_user(1))

