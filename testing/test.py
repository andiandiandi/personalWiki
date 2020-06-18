import os
from models.peewee.peewee import *
from models.peewee.playhouse import *
from models.peewee.playhouse.sqlite_ext import *
from models import models

import mistune
import json
import re

import mistletoe
from mistletoe.ast_renderer import ASTRenderer

Models = [models.File,models.Folder,models.Content]

def list_of_imagelinks(md_ast):
	image_objs = []
	for entry in md_ast:
		if "type" in entry:
			if entry["type"] == "image":
				image_objs.append(entry)
		if "children" in entry:
			image_objs += list_of_imagelinks(entry["children"])

	return image_objs

def list_of_textlinks(md_ast):
	image_objs = []
	for entry in md_ast:
		if "type" in entry:
			if entry["type"] == "link":
				image_objs.append(entry)
		if "children" in entry:
			image_objs += list_of_textlinks(entry["children"])

	return image_objs

def parseText(md_ast, d = None, p = 0):
	if d is None:
		d = {}
	for entry in md_ast:
		if "children" in entry:
			parseText(entry["children"],d=d,p=p)
			p+=1
		elif "text" in entry:
			if entry["text"]:
				for s in entry["text"].split():
					if s[0] in d:
						d[s[0]].append((s,p))
					else: 
						d[s[0]] = []
						d[s[0]].append((s,p))
	return d

def parseContent(content):
	markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
	tree = markdown(content)
	print(tree)
	return treeb

def parseContentMistletoe(content):
	tree = mistletoe.markdown(content, ASTRenderer)
	#print(tree)
	return tree

def initProject(db,model_dict, jsondata, parentID = None):
	persisted_Folder = model_dict["folder"].create(name=jsondata["name"],parentid=parentID)
	parentID = persisted_Folder.id
	subfolders = jsondata["folders"]
	files = jsondata["files"]
	#fill file table
	for file in files:
		full_path = file["path"]
		basename_no_extension = os.path.splitext(os.path.basename(full_path))[0]
		extension = os.path.splitext(full_path)[1]
		path = os.path.dirname(full_path)
		persisted_file = model_dict["file"].create(name=basename_no_extension,extension=extension,path=path, fullpath=full_path,folderid=parentID)

		tree = parseContentMistletoe(file["content"])
		#textdict = json.dumps(parseText(tree))
		#imagelinks = json.dumps(list_of_imagelinks(tree))
		#textlinks = json.dumps(list_of_textlinks(tree))
		textdict = ""
		textlinks = ""
		imagelinks = ""
		model_dict["content"].create(textdict = textdict, textlinks=textlinks,imagelinks=imagelinks,fileid=persisted_file.id)
		return
	#fill folder table
	for subfolder in subfolders:
		pass
		initProject(db,model_dict,subfolder,parentID)

class DbWrapper:
	def __init__(self):
		self.db = None

	def create_connection(self):
		try:
			self.db = SqliteExtDatabase(":memory:")
			self.db.connect()
		except Exception as e:
			print(e)
			return False

		return self.has_connection()

	def prepare_tables(self):
		self.drop_tables()
		self.create_tables()

	def has_connection(self):
		return bool(self.db)

	def drop_tables(self):
		with self.db.bind_ctx(Models):
			self.db.drop_tables(Models)

	def create_tables(self):
		with self.db.bind_ctx(Models):
			self.db.create_tables(Models)

	def initProject(self,json):
		with self.db.bind_ctx(Models):
			d = {}
			d["folder"] = models.Folder
			d["file"] = models.File
			d["content"] = models.Content
			initProject(self.db,d,json)

	def selFolders(self):
		with self.db.bind_ctx(Models):
			r = models.Folder.select()
			for f in r:	
				print(f.name)
				print(f.id)
				print(f.parentid)
				print("**********************************")

	def selFiles(self):
		with self.db.bind_ctx(Models):
			r = models.File.select()
			for f in r:
				print("id",f.id)
				print("name",f.name)
				print("ext",f.extension)
				print("path",f.path)
				print("full",f.fullpath)
				print("folderid:",f.folderid)
				print("___________________________")

	def getFile(self,id):
		with self.db.bind_ctx(Models):
			r = models.File.get_by_id(models.File.id==id)

	def query(self,id):
		with self.db.bind_ctx(Models):
			query = models.Content.select(models.Content.textdict,models.Content.textlinks,models.Content.imagelinks).join(models.File).where(models.File.id==0)
			for row in query:
				pass

w = DbWrapper()
w.create_connection()
w.prepare_tables()

jsondata = {"type": "folder", "files": [{"content": "- First item\n- Second item\n- Third item\n    - Indented item\n    - Indented item\n- Fourth item\n\n\njo\nfetten\n\ntest", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}], "folders": [{"type": "folder", "files": [], "folders": [], "name": "wikiconfig"}], "name": "testwiki"}



w.initProject(jsondata)

#todo
#json1 für sqlite
#oder
       
#iwie stringify links