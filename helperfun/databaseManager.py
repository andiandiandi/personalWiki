import sqlite3

connection = None

def create_connection():
	""" create a database connection to a SQLite database """
	global connection
	try:
		if connection:
			return connection
		else:
			connection = sqlite3.connect(":memory:")
	except Error as e:
		print(e)

	return connection

	
def create_table():
	global connection
	cursor = connection.cursor()
	cursor.execute("""Create Table employees (
			first text,
			second text,
			age integer
			)""")
	connection.commit()

def insert(fname,sname,age):
	global connection
	cursor = connection.cursor()
	cursor.execute("insert into employees values (:fname,:sname,:age)",{'fname':fname,'sname':sname,'age':age})
	connection.commit()

def sel():
	global connection
	cursor = connection.cursor()
	cursor.execute("select * from employees")
	print(cursor.fetchall())

create_connection()
create_table()
insert("a","b",1)
insert("lol","a",2)
sel()
