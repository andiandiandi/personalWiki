import sqlite3
import os
from . import wikiValidator
from . import pathManager

class Db:
	def __init__(self):
		pass



def db_existance_check():
	ValidationResult = wikiValidator.validate()

	if ValidationResult[0] == wikiValidator.ValidationResult.success:
		#db exists already
		path = os.path.join(ValidationResult[1],"stWiki.db")
		path_exists = pathManager.exists(path)
		if path_exists:
			return wikiValidator.ValidationResult.success, path
		else:
			return wikiValidator.ValidationResult.failure, path
	else:
		return ValidationResult

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

