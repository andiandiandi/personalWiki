from .peewee.peewee import *
from .peewee.playhouse.sqlite_ext import *

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
	name = CharField()
	extension = CharField()
	path = CharField()
	folderid = ForeignKeyField(Folder)

class Content(Model):
	# Full-text search index.
	id = AutoField()
	textdict = CharField()
	textlinks = CharField()
	imagelinks = CharField()
	headers = CharField()
	footnotes = CharField()
	fileid = ForeignKeyField(File)


modellist = [File,Folder,Content]
