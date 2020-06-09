import os
from .libs.peewee.peewee import *
from .libs.peewee.playhouse import *
from . import pathManager
from .models import models


class DbWrapper:
	def __init__(self, wiki):
		self.configpath = wiki.configpath
		self.path = os.path.join(self.configpath, "stWiki.db")
		self.db = None
		self.wiki = wiki

	def dbfile_exists(self):
		return pathManager.exists(self.path)

	def create_connection(self):
		try:
			self.db = SqliteDatabase(self.path)
			self.db.connect()
		except:
			print("db error")
			return False

		return self.has_connection()

	def has_connection(self):
		return bool(self.db)

	def drop_tables(self):
		with self.db.bind_ctx([models.File,models.FileRelation]):
			self.db.drop_tables([models.File, models.FileRelation])

	def create_tables(self):
		with self.db.bind_ctx([models.File,models.FileRelation]):
			self.db.create_tables([models.File, models.FileRelation])

	def build_model(self):
		with self.db.bind_ctx([models.File,models.FileRelation]):
			folder_file_dict = {}
			for folder, subs, files in os.walk(self.wiki.wikipath):
				folder_temp = models.File(name = os.path.basename(folder), filetype="folder", extension="", lastmodified=0)
				files_in_folder = []
				for filename in files:
					filetemp = models.File(name = filename, filetype="file", extension="", lastmodified=0)
					files_in_folder.append(filetemp)
				for f in files_in_folder:
					filerelation = models.FileRelation(container=folder_temp,containee=f)
					folder_file_dict[folder_temp] = filerelation

			

	def sel(self):
		with self.db.bind_ctx([models.File,models.FileRelation]):
			r2 = models.FileRelation.select()
			for relation in r2:
				print(relation.containee.name)

def test():
	return "db"