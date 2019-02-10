import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

def remove_tables():
	#attempt to drop tables IF they exist
	try:
 	   cursor.execute('DROP TABLE users')
	except:
 	   pass
	try:
 	   cursor.execute('DROP TABLE interval')
	except:
 	   pass

def create_tables():
	#create the tables
	cursor.execute('CREATE TABLE users ('
 	              'discordId INTEGER,'
  	             'timezone INTEGER)')

	cursor.execute('CREATE TABLE interval ('
 	              'id INTEGER,'
  	             'userId INTEGER,'
   	            'startDay INTEGER,'
    	           'startHour DOUBLE,'
     	          'endDay INTEGER,'
      	         'endHour DOUBLE)'
       	        )

def add_user(discordId, timezone):
	cursor.execute('INSERT INTO users (discordId, timezone) VALUES ('+
								str(discordId) + ", " +
								str(timezone) + ")")
	db.commit()

def add_interval(id, userId, startDay, startHour, endDay, endHour):
	cursor.execute('INSERT INTO interval (id, userId, startDay, startHour, endDay, endHour) VALUES ('+
								str(id) + ", " + 
								str(userId) + ", " +
								str(startDay) + ", " +
								str(startHour) + ", " +
								str(endDay) + ", " +
								str(endHour) + ")")
	db.commit()

def find_timezone(discordId):
	cursor.execute('SELECT timezone FROM users WHERE discordId = '+str(discordId))
	return cursor.fetchone()[0]

def find_interval_user(userId):
	cursor.execute('SELECT * FROM interval WHERE userId = ' + str(userId))
	return cursor.fetchall()


if __name__ ==' __main__':
	remove_tables()
	create_tables()
	add_user(1, 0)
	add_user(2, 3)
	add_interval(1, 1, 0, 9, 0, 12)
	add_interval(1, 1, 1, 7, 1, 10)
	add_interval(1, 2, 0, 4, 0, 9)
	print(find_timezone(1))
	print(find_interval_user(1))


