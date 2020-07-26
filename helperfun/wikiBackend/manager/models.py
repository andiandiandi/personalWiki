from .libs.peewee.peewee import *
from .libs.peewee.playhouse import hybrid

import os

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

class File(BaseModel):
	_fullpath = CharField(primary_key=True)
	_name = CharField()
	_extension = CharField()
	_relpath = CharField()
	lastmodified = FloatField()

	@hybrid.hybrid_property
	def fullpath(self):
		return self._fullpath

	@fullpath.setter
	def set_fullpath(self, fullpath):
		# code to process counter comes here
		self._fullpath = fullpath
		self._name = os.path.splitext(os.path.basename(fullpath))[0] or None
		self._extension = os.path.splitext(fullpath)[1] or None
		self._relpath = os.path.dirname(fullpath) or None

	@hybrid.hybrid_property
	def name(self):
		return self._name
	@hybrid.hybrid_property
	def extension(self):
		return self._extension
	@hybrid.hybrid_property
	def relpath(self):
		return self._relpath
		
class Content(Model):
	id = AutoField()
	textdict = CharField()
	textlinks = CharField()
	imagelinks = CharField()
	headers = CharField()
	footnotes = CharField()
	filepath = ForeignKeyField(File)
	rawString = CharField()


modellist = [File,Folder,Content,DatabaseMetadata]
