import os
from .libs.peewee.peewee import *
from .libs.peewee.playhouse import *
from .libs.peewee.playhouse.sqlite_ext import *
from . import models

import json

from . import searchDataParser

from .libs import mistletoe
from .libs.mistletoe.ast_renderer import ASTRenderer


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

def list_of_headers(md_ast):
	objs = []
	if "type" in md_ast:
		if "Heading" in md_ast["type"]:
			objs.append(md_ast)
	if "children" in md_ast:
		for child in md_ast["children"]:
			objs += list_of_headers(child)

	return objs

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
			span = footnote_ast[2] if 0 <= 1 < len(footnote_ast) else ""
			objs.append({"name":footnote, "target":target, "title":title, "span": span})

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

def parseContentMistletoe(content):
	tree = mistletoe.markdown(content, ASTRenderer)
	#print(tree)
	return tree

def extractFiles(jsondata):
	f = []
	if "files" in jsondata:
		f += jsondata["files"]
	if "folders" in jsondata:
		for folder in jsondata["folders"]:
			f += extractFiles(folder)

	return f

class DbWrapper:
	def __init__(self,wiki):
		self.db = None
		self.wiki = wiki
		self.modeldict = {}
		self.modeldict["folder"] = models.Folder
		self.modeldict["file"] = models.File
		self.modeldict["content"] = models.Content

	def create_connection(self):
		try:
			self.db = SqliteExtDatabase(os.path.join(self.wiki.root_folder,"wikiconfig","wiki.db"))
			self.db.connect()
		except Exception as e:
			print(e)
			return False

		return self.hasConnection()

	def resetTables(self):
		self.dropTables()
		self.createTables()

	def hasConnection(self):
		return bool(self.db)

	def checkIndex(self,json_project_structure):
		filesJson = extractFiles(json_project_structure)


		#self.dropTables()
		self.createTables()

		dbFiles = self.selFiles()

		for dbFile in list(dbFiles):
			for file in list(filesJson):
				fullPath = file["path"]
				if dbFile.fullpath == fullPath:
					upToDate = file["lastmodified"] == dbFile.lastmodified
					if not upToDate:
						self.updateFile(dbFile.id,file)
						print("updated",file["path"])
						print(models.Content.get(models.Content.fileid == dbFile.id).headers)
					else:
						print("file is up to date",file["path"])
						print(models.Content.get(models.Content.fileid == dbFile.id).headers)

					filesJson.remove(file)
					dbFiles.remove(dbFile)
					break
			


		#leftovers in db
		if dbFiles:
			for f in dbFiles:
				print("deleting leftover",f.fullpath)
				associatedContent = models.Content.get(models.Content.fileid == f.id)
				f.delete_instance()
				associatedContent.delete_instance()


		if filesJson:
			for f in filesJson:
				print("inserting new file",f["path"])
				self.insertFile(f)

		return True

	def saveFile(self,jsonfile):
		file = models.File.get_or_none(models.File.fullpath == jsonfile["path"])
		if file:
			self.updateFile(file.id,jsonfile)
		else:
			self.insertFile(jsonfile)

	def filesChanged(self,queueDict):
		q = queueDict["queue"]
		return json.dumps(q)

	def clearDatabase(self):
		try:
			self.dropTables()
			return {"status":"success",
					"response": "database cleared"}
		except Exception as E:
			return {"status":"exception",
					"response": str(E)}

	def dropTables(self):
		with self.db.bind_ctx(models.modellist):
			self.db.drop_tables(models.modellist)

	def createTables(self):
		with self.db.bind_ctx(models.modellist):
			self.db.create_tables(models.modellist, safe=True)

	def initializeProject(self,json):
		with self.db.bind_ctx(models.modellist):
			initProject(self.db,self.modeldict,json)

	def updateFile(self,fileid,jsonfile):
		with self.db.bind_ctx(models.modellist):
			fileupdateQuery = models.File.update(lastmodified = jsonfile["lastmodified"]).where(models.File.id == fileid)
			rows = fileupdateQuery.execute()
			if rows > 0:
				tree = parseContentMistletoe(jsonfile["content"])
				#textdict = json.dumps(parseText(tree))
				imagelinks = json.dumps(list_of_imagelinks(json.loads(tree)))
				textlinks = json.dumps(list_of_textlinks(json.loads(tree)))
				textdict = ""
				headers = json.dumps(list_of_headers(json.loads(tree)))
				footnotes = json.dumps(list_of_footnotes(json.loads(tree)))
				contentupdateQuery = models.Content.update(textdict = textdict, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes).where(models.Content.fileid == fileid)
				contentupdateQuery.execute()


	def insertFile(self,jsonfile):
		fullpath = jsonfile["path"]
		basename_no_extension = os.path.splitext(os.path.basename(fullpath))[0]
		extension = os.path.splitext(fullpath)[1]
		relpath = os.path.dirname(fullpath)
		lastmodified = jsonfile["lastmodified"]
		#persisted_file = self.modeldict["jsonfile"].create(fullpath = fullpath, name=basename_no_extension,extension=extension,relpath=relpath, lastmodified = lastmodified, folderid=parentID)
		persisted_file = self.modeldict["file"].create(fullpath = fullpath, name=basename_no_extension,extension=extension,relpath=relpath, lastmodified = lastmodified)

		tree = parseContentMistletoe(jsonfile["content"])
		#textdict = json.dumps(parseText(tree))
		imagelinks = json.dumps(list_of_imagelinks(json.loads(tree)))
		textlinks = json.dumps(list_of_textlinks(json.loads(tree)))
		textdict = ""
		headers = json.dumps(list_of_headers(json.loads(tree)))
		footnotes = json.dumps(list_of_footnotes(json.loads(tree)))
		c = self.modeldict["content"].create(textdict = textdict, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes, fileid=persisted_file.id)

	def selFolders(self):
		with self.db.bind_ctx(models.modellist):
			r = models.Folder.select()
			for f in r:	
				print(f.name)
				print(f.id)
				print(f.parentid)
				print("**********************************")

	def selFiles(self):
		with self.db.bind_ctx(models.modellist):
			r = models.File.select()
			l = []
			for f in r:
				#print("id",f.id)
				#print("name",f.name)
				#print("ext",f.extension)
				#print("path",f.relpath)
				print("full",f.fullpath)
				#print("folderid:",f.folderid)
				#print("___________________________")
				l.append(f)
			return l

	def getFile(self,fullPath, id = None):
		with self.db.bind_ctx(models.modellist):
			if id:
				query = models.File.get_by_id(models.File.id==id)
				if query.exists():
					return query
			else:
				file = models.File.get_or_none(models.File.fullpath == fullPath)
				if file:
					return file
				return None

	def initProject(self,db, jsondata, parentID = None):
		persisted_Folder = self.modeldict["folder"].create(name=jsondata["name"],parentid=parentID)
		parentID = persisted_Folder.id
		subfolders = jsondata["folders"]
		files = jsondata["files"]
		#fill file table
		for file in files:
			fullpath = file["path"]
			basename_no_extension = os.path.splitext(os.path.basename(fullpath))[0]
			extension = os.path.splitext(fullpath)[1]
			relpath = os.path.dirname(fullpath)
			lastmodified = file["lastmodified"]
			#persisted_file = self.modeldict["file"].create(fullpath = fullpath, name=basename_no_extension,extension=extension,relpath=relpath, lastmodified = lastmodified, folderid=parentID)
			persisted_file = self.modeldict["file"].create(fullpath = fullpath, name=basename_no_extension,extension=extension,relpath=relpath, lastmodified = lastmodified)

			tree = parseContentMistletoe(file["content"])
			#textdict = json.dumps(parseText(tree))
			imagelinks = json.dumps(list_of_imagelinks(json.loads(tree)))
			textlinks = json.dumps(list_of_textlinks(json.loads(tree)))
			textdict = ""
			headers = json.dumps(list_of_headers(json.loads(tree)))
			footnotes = json.dumps(list_of_footnotes(json.loads(tree)))
			c = self.modeldict["content"].create(textdict = textdict, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes, fileid=persisted_file.id)
		#fill folder table
		for subfolder in subfolders:
			initProject(db,self.modeldict,subfolder,parentID)

	def query(self,id):
		with self.db.bind_ctx(models.modellist):
			query = models.Content.select(models.Content.textdict,models.Content.textlinks,models.Content.imagelinks,models.Content.headers,models.Content.footnotes).join(models.File).where(models.File.id==id)
			for row in query:
				print(row.textlinks)
				print("______________")
				print(row.imagelinks)
				print("___________")
				print(row.headers)
				print("___________")
				print(row.footnotes)

	def query2(self):
		with self.db.bind_ctx(models.modellist):
			query = (models.File
			         .select(models.File.name,models.Content.imagelinks)
			         .join(models.Content, JOIN.LEFT_OUTER)  # Joins user -> tweet.
			         .group_by(models.File.name))

			for row in query:
				print(row.name)
				print(row.content.imagelinks)

				break
				for footnote in json.loads(row.footnotes):
					if footnote["name"] == "logo" and footnote["title"] is not "test":
						print(row.file.name)

	def query3(self):
		with self.db.bind_ctx(models.modellist):
			query = models.Content.select(models.Content.footnotes,models.Content.id).join(models.File)
			for row in query:
				for footnote in json.loads(row.footnotes):
					if footnote["name"] == "logo" and footnote["title"] is not "test":
						print(row.id)

	def isOrphan(self,filename, extension):
		with self.db.bind_ctx(models.modellist):
			query = models.Content.select(models.Content.textlinks)
			for row in query:
				for element in json.loads(row.textlinks):
					if element["target"] == filename + extension:
						return False
			else:
				return True

	def runSearchQuery(self,jsondata):
		print(jsondata)
		print()
		if "files" in jsondata and "element" in jsondata and "values" in jsondata:
			files = jsondata["files"]
			element = jsondata["element"]
			values = jsondata["values"]
			return searchDataParser.elementHandlers[element["value"]](files,element,values,self.db)
		else:
			raise Exception('"files" or "values" key not existent')