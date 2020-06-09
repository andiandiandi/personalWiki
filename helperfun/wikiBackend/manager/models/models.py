from ..libs.peewee.peewee import *

db = None

class BaseModel(Model):
	class Meta:
		database = db

class File(BaseModel):
	name = CharField()
	filetype = CharField()
	extension = CharField()
	lastmodified = IntegerField()

class FileRelation(BaseModel):
	container = ForeignKeyField(File)
	containee = ForeignKeyField(File)

