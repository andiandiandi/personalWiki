from .libs.peewee.peewee import *

db = None

class BaseModel(Model):
	class Meta:
		database = db

class Folder(BaseModel):
	name = CharField()
	id = AutoField()
	parentid = ForeignKeyField("self", null = True, backref = "children")

class File(BaseModel):
	id = AutoField()
	fullpath = CharField()
	name = CharField()
	extension = CharField()
	relpath = CharField()
	lastmodified = FloatField()

class Content(Model):
	id = AutoField()
	textdict = CharField()
	textlinks = CharField()
	imagelinks = CharField()
	headers = CharField()
	footnotes = CharField()
	fileid = ForeignKeyField(File)


modellist = [File,Folder,Content]
