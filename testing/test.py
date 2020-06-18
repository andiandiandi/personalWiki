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
	objs = []
	if "type" in md_ast:
		if md_ast["type"] == "Image":
			objs.append(md_ast)
	if "children" in md_ast:
		for child in md_ast["children"]:
			objs += list_of_imagelinks(child)

	return objs

def list_of_textlinks(md_ast):
	objs = []
	if "type" in md_ast:
		if "Link" in md_ast["type"]:
			objs.append(md_ast)
	if "children" in md_ast:
		for child in md_ast["children"]:
			objs += list_of_textlinks(child)

	return objs

def extract_footnote_information(name,footnote_ast):
	return 


def list_of_footnotes(md_ast,footnotes = False):
	objs = []
	if not footnotes:
		if "footnotes" in md_ast:
			objs += list_of_footnotes(md_ast["footnotes"],footnotes = True)
	else:
		for footnote in md_ast:
			footnote_ast = md_ast[footnote]
			target = footnote_ast[0] if 0 <= 0 < len(footnote_ast) else ""
			title = footnote_ast[1] if 0 <= 1 < len(footnote_ast) else ""
			objs.append({"name":footnote, "target":target, "title":title})

	return objs

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
		imagelinks = json.dumps(list_of_imagelinks(json.loads(tree)))
		textlinks = json.dumps(list_of_textlinks(json.loads(tree)))
		textdict = ""
		footnotes = json.dumps(list_of_footnotes(json.loads(tree)))
		c = model_dict["content"].create(textdict = textdict, textlinks=textlinks,imagelinks=imagelinks,footnotes = footnotes, fileid=persisted_file.id)
	#fill folder table
	for subfolder in subfolders:
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
			return r

	def query(self,id):
		with self.db.bind_ctx(Models):
			query = models.Content.select(models.Content.textdict,models.Content.textlinks,models.Content.imagelinks,models.Content.footnotes).join(models.File).where(models.File.id==id)
			for row in query:
				print(row.textlinks)
				print("______________")
				print(row.imagelinks)
				print("___________")
				print(row.footnotes)

w = DbWrapper()
w.create_connection()
w.prepare_tables()

jsondata = {"type": "folder", "files": [{"content": "[I'm an inline-style link](https://www.google.com)\n\n[I'm an inline-style link with title](https://www.google.com \"Google's Homepage\")\nInline-style: \n![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 1\")\n\n[I'm a reference-style link][Arbitrary case-insensitive reference text]\n\n[I'm a relative reference to a repository file](../blob/master/LICENSE)\n\n[You can use numbers for reference-style link definitions][1]\n\nReference-style: \n![alt text][logo]\n\nOr leave it empty and use the [link text itself].\n\nURLs and URLs in angle brackets will automatically get turned into links. \nhttp://www.example.com or <http://www.example.com> and sometimes \nexample.com (but not on Github, for example).\n\nSome text to show that the reference links can follow later.\n\nHere's our logo (hover to see the title text):\n\n\n\n\n\n\n\n[arbitrary case-insensitive reference text]: https://www.mozilla.org\n[1]: http://slashdot.org\n[link text itself]: http://www.reddit.com\n[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 2\"", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}], "folders": [{"type": "folder", "files": [], "folders": [], "name": "wikiconfig"}], "name": "testwiki"}



w.initProject(jsondata)
w.query(1)