from .libs.peewee.peewee import *

from .libs.peewee.playhouse import hybrid

from random import randrange
import os
import inspect

db = None

class BaseModel(Model):
	class Meta:
		database = db

class DatabaseMetadata(BaseModel):
	pluginversion = FloatField()

class Folder(BaseModel):
	name = CharField()
	id = AutoField()
	parentid = ForeignKeyField("self", null = True, backref = "children")

class Image(BaseModel):
	id = AutoField()
	base64 = CharField()
	fileid = ForeignKeyField(File, on_delete = 'CASCADE')

class File(BaseModel):
	id = AutoField(primary_key=True)
	fullpath = CharField(column_name='fullpath')
	name = CharField(column_name='name')
	extension = CharField(column_name='extension')
	relpath = CharField(column_name='relpath')
	lastmodified = FloatField(column_name='lastmodified')

	@hybrid.hybrid_method
	def fileIn(self,filesv):
		filename = self.name.concat(self.extension)
		return filename.in_(filesv)

class Content(Model):
	id = AutoField()
	textdict = CharField()
	textlinks = CharField()
	imagelinks = CharField()
	headers = CharField()
	footnotes = CharField()
	fileid = ForeignKeyField(File, on_delete = 'CASCADE')
	rawString = CharField()


modellist = [File,Image,Folder,Content,DatabaseMetadata]
