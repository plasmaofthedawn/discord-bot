import sqlite3

db = sqlite3.connect('database.db')

cursor = db.cursor()

#attempt to drop tables IF they exist
try:
    cursor.execute('DROP TABLE users')
except:
    pass
try:
    cursor.execute('DROP TABLE interval')
except:
    pass

#create the tables
cursor.execute('CREATE TABLE users ('
               'discordId INTEGER,'
               'timeZone INTEGER)')

cursor.execute('CREATE TABLE interval ('
               'id INTEGER'
               'userId INTEGER'
               'startDay INTEGER'
               'startHour DOUBLE'
               'endDay INTEGER'
               'endHOUR DOUBLE)'
               )