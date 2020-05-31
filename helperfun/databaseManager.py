import sqlite3
import os
import imp
from . import configManager
from . import pathManager

imp.reload(configManager)
imp.reload(pathManager)

class Db:
	def __init__(self,configpath):
		self.configpath = configpath
		self.path = os.path.join(self.configpath, "stWiki.db")
		self.connection = None

	def init(self):
		self.create_connection()
		#exists = self.check_existance()
		#if not exists:
		#	exists = 

	def check_existance(self):
		return pathManager.exists(self.path)

	def create_connection(self):
		try:
			if self.connection:
				return connection
			else:
				self.connection = sqlite3.connect(self.path)
		except Error as e:
			print(e)

		return self.has_connection()

	def has_connection(self):
		return bool(self.connection)

	def create_table(self):
		cursor = self.connection.cursor()
		cursor.execute("""Create Table employees (
				first text,
				age integer
				)""")
		self.connection.commit()

	def drop_table(self):
		cursor = self.connection.cursor()
		cursor.execute('drop table if exists employees')
		self.connection.commit()

	def has_table(self):
		
		cursor = self.connection.cursor()
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
		return bool(cursor.fetchall())

	def insert(self,fname,age):
		cursor = self.connection.cursor()
		cursor.execute("insert into employees values (:fname,:age)",{'fname':fname, 'age':age})
		self.connection.commit()

	def remove_entry(self):
		list = self.sel()
		print(list)
		item = list[0]
		sql = 'DELETE FROM employees WHERE age=?'
		cursor = self.connection.cursor()
		cursor.execute(sql, (item[1],))
		self.connection.commit()
		print(self.sel())

	def sel(self):
		cursor = self.connection.cursor()
		cursor.execute("select * from employees")
		return cursor.fetchall()
	


