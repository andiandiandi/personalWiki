from .libs.peewee.peewee import *

from .libs.peewee.playhouse import hybrid

from random import randrange
import os
import inspect

from . import pathManager

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

class Image(BaseModel):
	id = AutoField()
	base64 = CharField()
	mimetype = CharField()
	fileid = ForeignKeyField(File, on_delete = 'CASCADE')

class Content(Model):
	id = AutoField()
	textdict = CharField()
	#[{"type": "Link", "target": "wikipage.md", "title": "", "children": [{"type": "RawText", "content": "wikilink", "span": {"start": 5, "read": 1}}], "span": {"start": 5, "read": 1}}]
	textlinks = CharField()
	imagelinks = CharField()
	headers = CharField()
	footnotes = CharField()
	wordsCharsReadtime = CharField()
	fileid = ForeignKeyField(File, on_delete = 'CASCADE')
	rawString = CharField()

	@classmethod
	def hasWikilink(self,targetFullpath,currentFullpath,textlinksListDict):
		currentRelpath = pathManager.relpath(currentFullpath)

		for entry in textlinksListDict:
			wikilink = entry["target"]
			try:
				normpath = os.path.normpath(os.path.join(currentRelpath,wikilink))
				if normpath == targetFullpath:
					return True
			except:
				continue

		return False	

modellist = [File,Image,Folder,Content,DatabaseMetadata]
