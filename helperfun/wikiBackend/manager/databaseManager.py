import os
from .libs.peewee.peewee import *
from .libs.peewee.playhouse import *
from .libs.peewee.playhouse.sqlite_ext import *
from . import models

import json
import time
import re
import threading

from . import responseGenerator
from . import sessionManager
from . import pathManager
from .pathManager import Filetype
from . import multiPurposeParser
from . import projectListener
from . import wordCount

class DatabaseWrapper:
	def __init__(self, root_folder, sid, callbackError):
		self.db = None
		self.root_folder = root_folder
		self.sid = sid
		self.callbackError = callbackError
		self.modeldict = {}
		self.modeldict["file"] = models.File
		self.modeldict["content"] = models.Content
		self.modeldict["image"] = models.Image
		self.modeldict["searchquery"] = models.SearchQuery

	def create_connection(self):
		try:
			self.db = SqliteExtDatabase(os.path.join(self.root_folder,"wikiconfig","wiki.db"), pragmas={'foreign_keys': 1})
			self.db.connect()
		except Exception as e:
			print("exception while connint to db:",str(e))
			return False

		return self.hasConnection()

	def closeConnection(self):
		self.db.close()

	def resetTables(self):
		self.dropTables()
		self.createTables()

	def hasConnection(self):
		return bool(self.db)

	def deleteFile(self, fullpath):
		with self.db.bind_ctx(models.modellist):
			fileInDb = self.getFile(fullpath)
			if not fileInDb:
				return responseGenerator.createExceptionResponse("could not delete file, file not found: " + fullpath)

			"""
			try:
				associatedContent = models.Content.get(models.Content.fileid == fileInDb.id)
				associatedContent.delete_instance()
			"""
			try:
				fileInDb.delete_instance()

				return responseGenerator.createSuccessResponse("deleted file: " + fullpath)
			except Exception as E:
				return responseGenerator.createExceptionResponse("could not delete file: " + fullpath + " | " + str(E))

	def tablesExist(self):
		with self.db.bind_ctx(models.modellist):
			if self.db:
				requirementTables = ['file', 'image','content']
				tables = self.db.get_tables()
				return set(requirementTables) <= set(tables)

			return False

	def moveFile(self, srcPath, destPath, lastmodified):
		with self.db.bind_ctx(models.modellist):
			try:
				fileInDb = self.getFile(srcPath)
				if not fileInDb:
					return responseGenerator.createExceptionResponse("could not move file, file not found: " + srcPath)
				fileWithDestPath = self.getFile(destPath)
				if fileWithDestPath:
					return responseGenerator.createExceptionResponse("could not move file, file with destination path already exists: " + destPath)

				name = pathManager.filename(destPath)
				extension = pathManager.extension(destPath)
				relpath = pathManager.relpath(destPath)
				updateFileQuery = models.File.update(fullpath=destPath,name=name,extension=extension,relpath=relpath,lastmodified=lastmodified).where(models.File.fullpath == srcPath)
				updateFileQuery.execute()

				if os.path.dirname(srcPath) == os.path.dirname(destPath):
					response = self.fileRenamedTrigger(srcPath,destPath,pathManager.extensionNoDot(srcPath))
					
					sessionManager.notifySubscribers("rename_wikipage",self.sid,path=srcPath,jsondata=destPath)
					if response["status"] == "exception":
						return response


				return responseGenerator.createSuccessResponse("moved file: " + json.dumps({"srcpath":srcPath,"destpath":destPath,"lastmodified":lastmodified}))


			except Exception as E:
				return responseGenerator.createExceptionResponse("could not move file: " + srcPath + " to " + destPath + " | " + str(E))

	def fileRenamedTrigger(self, srcPath, destPath, mimetype):
		with self.db.bind_ctx(models.modellist):
			try:
				if pathManager.filetype(mimetype) == Filetype.wikipage:
					#query = (models.Content.select(models.Content.textlinks,models.Content.fileid,models.Content.rawString).join(models.File).where(models.Content.hasWikilink(srcPath,models.File.fullpath)))
					l = []
					pathContentL = {}

					query = (models.File.select(models.Content.textlinks,models.File.fullpath).join(models.Content))
					for file in query:
						try:
							d = json.loads(file.content.textlinks)
							l.append((srcPath,file.fullpath,d))
							print("APPEND",(srcPath,file.fullpath,d))
						except:
							continue
					for item in l:
						hasWikilink = models.Content.hasWikilink(item[0],item[1],item[2])						
						if hasWikilink:
							pathContentL[item[1]] = self.getContent(None,fullpath = item[1]).rawString

					replacee = pathManager.basename_w_ext_of_path(srcPath)
					toreplace = pathManager.basename_w_ext_of_path(destPath)

					for path, rawContent in pathContentL.items():
						pathContentL[path] = rawContent.replace(replacee,toreplace)
						print("REPLACED " + str(replacee) + " with " + str(toreplace) + " in " + path)


					print("IPDATE",pathContentL)

					t1 = threading.Thread(target=pathManager.writeFiles, args=(pathContentL,))
					t1.start()
					t1.join()


				elif pathManager.filetype(mimetype) == Filetype.image:
					pass


				return responseGenerator.createSuccessResponse("executed Trigger on 'file renamed'")
			except Exception as E:
				return responseGenerator.createExceptionResponse("Exception at Trigger on 'file renamed': " + srcPath + " | " + type(E).__name__)

	def updateFile(self,path, content, lastmodified,mimetype):
		with self.db.bind_ctx(models.modellist):
			fileInDb = self.getFile(path)
			if not fileInDb:
				return responseGenerator.createExceptionResponse("File not found in database: " + path)
			
			if fileInDb.lastmodified == lastmodified:
				return responseGenerator.createSuccessResponse("file already up to date: " + path)
			fileupdateQuery = models.File.update(lastmodified = lastmodified).where(models.File.fullpath == path)
			rows = fileupdateQuery.execute()
			if rows > 0:
				response = None
				if pathManager.filetype(mimetype) == Filetype.wikipage:
					response = self.updateWikipage(fileInDb.id,content)
				elif pathManager.filetype(mimetype) == Filetype.image:
					response = self.updateImage(fileInDb.id,content)

				if response["status"] == "exception":
					return response 

				return responseGenerator.createSuccessResponse("updated file: " + path)

			return responseGenerator.createExceptionResponse("could not update file: " + path)

	def updateImage(self,fileid,content):
		with self.db.bind_ctx(models.modellist):
			try:
				contentupdateQuery = models.Image.update(base64 = content).where(models.Image.fileid == fileid)
				contentupdateQuery.execute()

				return responseGenerator.createSuccessResponse("updated image with fileid: " + str(fileid))

			except Exception as E:
				return responseGenerator.createExceptionResponse("exception while updating image: " + str(E))


	def updateWikipage(self,fileid,content):
		with self.db.bind_ctx(models.modellist):
			try:
				tree = multiPurposeParser.parseContentMistletoe(content)
				dictTree = json.loads(tree)
				imagelinks = json.dumps(multiPurposeParser.list_of_imagelinks(dictTree))
				textlinks = json.dumps(multiPurposeParser.list_of_textlinks(dictTree))
				headers = json.dumps(multiPurposeParser.list_of_headers(dictTree))
				footnotes = json.dumps(multiPurposeParser.list_of_footnotes(dictTree))
				wordsCharsReadtime = json.dumps(wordCount.countWordsCharReadtime(content))
				w = multiPurposeParser.createWordHash(multiPurposeParser.textDict(dictTree))
				wordhash = json.dumps(w)
				contentupdateQuery = models.Content.update(wordhash=wordhash, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes, rawString = content, wordsCharsReadtime=wordsCharsReadtime).where(models.Content.fileid == fileid)
				contentupdateQuery.execute()

				return responseGenerator.createSuccessResponse("updated wikipage with fileid: " + str(fileid))

			except Exception as E:
				return responseGenerator.createExceptionResponse("exception while updating wikipage: " + str(E))


	def insertFile(self,path,content,lastmodified,mimetype):
		with self.db.bind_ctx(models.modellist):
			try:
				fileExists = self.getFile(path)
				if fileExists:
					return self.updateFile(path,content,lastmodified,mimetype)
				name = pathManager.filename(path)
				extension = pathManager.extension(path)
				relpath = pathManager.relpath(path)
				#persisted_file = self.modeldict["jsonfile"].create(fullpath = fullpath, name=basename_no_extension,extension=extension,relpath=relpath, lastmodified = lastmodified, folderid=parentID)
				persisted_file = self.modeldict["file"].create(fullpath = path, name = name, extension = extension, relpath = relpath, lastmodified = lastmodified)
			
				response = None
				if pathManager.filetype(mimetype) == Filetype.wikipage:
					response = self.insertWikipage(persisted_file.id,content)
				elif pathManager.filetype(mimetype) == Filetype.image:
					response = self.insertImage(persisted_file.id,content,mimetype)

				if response["status"] == "exception":
					return response

				return responseGenerator.createSuccessResponse("inserted file with content: " + path)

			except Exception as E:
				return responseGenerator.createExceptionResponse("exception while inserting file: " + path + " | " + str(E))

	def insertImage(self,fileid,content,mimetype):
		with self.db.bind_ctx(models.modellist):
			try:
				c = self.modeldict["image"].create(base64 = content,mimetype = mimetype,fileid=fileid)


				return responseGenerator.createSuccessResponse("inserted image : " + str(fileid))
			except Exception as E:
				return responseGenerator.createExceptionResponse("exception while inserting image: " + str(E))

	def insertWikipage(self,fileid,content):
		with self.db.bind_ctx(models.modellist):
			try:
				tree = multiPurposeParser.parseContentMistletoe(content)
				dictTree = json.loads(tree)
				imagelinks = json.dumps(multiPurposeParser.list_of_imagelinks(dictTree))
				textlinks = json.dumps(multiPurposeParser.list_of_textlinks(dictTree))
				headers = json.dumps(multiPurposeParser.list_of_headers(dictTree))
				footnotes = json.dumps(multiPurposeParser.list_of_footnotes(dictTree))
				wordsCharsReadtime = json.dumps(wordCount.countWordsCharReadtime(content))
				w = multiPurposeParser.createWordHash(multiPurposeParser.textDict(dictTree))
				wordhash = json.dumps(w)
				c = self.modeldict["content"].create(wordhash=wordhash, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes, rawString = content,wordsCharsReadtime=wordsCharsReadtime,fileid=fileid)

				return responseGenerator.createSuccessResponse("inserted wikipage:" + str(fileid))

			except Exception as E:
				return responseGenerator.createExceptionResponse("exception while inserting wikipage: " + str(E))

	def clearDatabase(self):
		try:
			self.dropTables()
			return responseGenerator.createSuccessResponse("Database cleared")
		except Exception as E:
			return responseGenerator.createExceptionResponse(str(E))

	def dropTables(self):
		with self.db.bind_ctx(models.modellist):
			self.db.drop_tables(models.modellist)

	def createTables(self):
		with self.db.bind_ctx(models.modellist):
			self.db.create_tables(models.modellist, safe=True)

	def selContent(self):
		with self.db.bind_ctx(models.modellist):
			try:
				r = models.Content.select()
				l = []
				for f in r:	
					try:
						l.append({
							"fullpath":str(f.fileid),
							"rawString":str(f.rawString),
							"headers":str(f.headers)
							})
					except Exception as E:
						continue
				return l
			except Exception as e:
				return str(e)


	def selFilesDEBUG(self):
		with self.db.bind_ctx(models.modellist):
			try:
				r = models.File.select()
				l = []
				for f in r:	
					l.append(f.fullpath)
					l.append(f.relpath)
					l.append(f.name)
					l.append(f.extension)
				return l
			except Exception as e:
				return str(e)
	
	def selImagesDEBUG(self):
		with self.db.bind_ctx(models.modellist):
			try:
				r = models.Image.select()
				l = []
				for f in r:	
					l.append(f.base64)
					l.append(f.mimetype)
				return l
			except Exception as e:
				return str(e)

	def selFiles(self):
		with self.db.bind_ctx(models.modellist):
			r = models.File.select()
			l = []
			for f in r:
				#print("id",f.id)
				#print("name",f.name)
				#print("ext",f.extension)
				#print("path",f.relpath)
				#print("folderid:",f.folderid)
				#print("___________________________")
				l.append(f)
			return l

	def selFilenames(self):
		with self.db.bind_ctx(models.modellist):
			r = models.File.select()
			l = []
			for f in r:
				l.append(f.fullpath)
			return l

	def selAllFullpathFromImage(self):
		with self.db.bind_ctx(models.modellist):
			imageQuery = models.File.select(models.File.fullpath).join(models.Image).where(models.File.id==models.Image.fileid)
			l = []
			for file in imageQuery:
				try:
					l.append(file.fullpath)
				except Exception as E:
					return responseGenerator.createExceptionResponse("could not select all Fullpaths from Image-Entity")
			return l

	def selFullpathFromFile(self,filename):
		with self.db.bind_ctx(models.modellist):
			fileQuery = models.File.select(models.File.fullpath).where(models.File.name == filename)
			l = []
			for file in fileQuery:
				try:
					l.append(file.fullpath)
				except Exception as E:
					return responseGenerator.createExceptionResponse("could not select Fullpath")
			return l

	def selImageData(self,filepathList):
		with self.db.bind_ctx(models.modellist):
			query = (models.File.select(models.File.fullpath,models.Image.base64,models.Image.mimetype)
								.join(models.Image).where(models.File.fullpath.in_(filepathList)))
			l = []
			for row in query:
				try:
					l.append({"fullpath":row.fullpath,"base64":row.image.base64,"mimetype":row.image.mimetype})
				except Exception as E:
					return responseGenerator.createExceptionResponse("could not select Image-Entity data")

			return l

	def selFulltextsearchMetadata(self,files_exclude,files):
		if files_exclude:
				query = models.File.select(models.File.fullpath,models.Content.wordhash).join(models.Content).where(~models.File.fileIn(files))
		else:
			if files:
				query = models.File.select(models.File.fullpath,models.Content.wordhash).join(models.Content).where(models.File.fileIn(files))
			else:
				query = models.File.select(models.File.fullpath,models.Content.wordhash).join(models.Content)

		l = []
		for row in query:
			try:
				l.append({"fullpath":row.fullpath,"wordhash":row.content.wordhash})
			except Exception as E:
				return responseGenerator.createExceptionResponse("could not select selFulltextsearch metadata")

		return l

	def selWordsCharsReadtime(self):
		with self.db.bind_ctx(models.modellist):
			query = models.File.select(models.Content.wordsCharsReadtime).join(models.Content)
			l = []
			for row in query:
				try:
					wordsCharsReadtime = json.loads(row.content.wordsCharsReadtime)
					l.append(wordsCharsReadtime)
				except Exception as E:
					return responseGenerator.createExceptionResponse("could not select WordsCharsReadtime")

			return l

	def getFile(self,fullPath):
		with self.db.bind_ctx(models.modellist):
			file = models.File.get_or_none(models.File.fullpath == fullPath)
			if file:
				return file
			return None

	def getContent(self, fileid, fullpath = None):
		with self.db.bind_ctx(models.modellist):
			if fullpath:
				file = self.getFile(fullpath)
				if file:
					fileid = file.id
				else:
					return None
			content = models.Content.get_or_none(models.Content.fileid == fileid)
			if content:
				return content
			return None

	def getSearchQuery(self,searchQuery):
		with self.db.bind_ctx(models.modellist):
			q = models.SearchQuery.get_or_none(models.SearchQuery.rawString == searchQuery)
			if q:
				return q
			return None

	def handleDeletedDirectoryGuess(self, deletedParentPath):
		try:
			with self.db.bind_ctx(models.modellist):
				query = models.File.select(models.File.fullpath)
				for entry in query:
					if pathManager.path_is_parent(deletedParentPath, entry.fullpath):
						self.deleteFile(entry.fullpath)

			return responseGenerator.createSuccessResponse("handled deleted directory guess successfully")
		except Exception as E:
			return responseGenerator.createExceptionResponse("could not handle directory deleted guess | " + str(E) + " | " + type(E).__name__)


	def listSearchQuery(self, root_folder):
		with self.db.bind_ctx(models.modellist):
			try:
				searchQuery = models.SearchQuery.select(models.SearchQuery.rawString,
														models.SearchQuery.creationdate)
				l = []
				for row in searchQuery:
					l.append({"rawString":row.rawString,"creationdate":row.creationdate})
				return responseGenerator.createSuccessResponse(l)
			except Exception as E:
				return responseGenerator.createExceptionResponse("could not list search queries: " + str(E) + " | " + type(E).__name__)

	def addSearchQuery(self,queryString):
		with self.db.bind_ctx(models.modellist):
			c = self.modeldict["searchquery"].create(rawString = queryString,creationdate = int(round(time.time() * 1000)))

	def deleteSavedQuery(self,queryString):
		with self.db.bind_ctx(models.modellist):
			searchQuery = self.getSearchQuery(queryString)
			if not searchQuery:
				return responseGenerator.createExceptionResponse("could not delete queryString: " + str(queryString) + " | " + "query-string not found in database")
			else:
				try:
					searchQuery.delete_instance()
					return responseGenerator.createSuccessResponse({"type":"deleted", "data":str(queryString)})
				except Exception as E:
					return responseGenerator.createExceptionResponse("could not remove search-query: " + str(queryString) + " | " + str(type(E).__name__))

class Indexer:
	def __init__(self, root_folder, sid, databaseWrapper, callbackError, wiki):
		self.root_folder = root_folder
		self.sid = sid
		self.databaseWrapper = databaseWrapper
		self.callbackError = callbackError
		self.FileSystemWatcher = None
		self.wiki = wiki
		

	def initialize(self):
		return self.startFileSystemWatcher()

	def cleanup(self):
		if self.FileSystemWatcher:
			self.FileSystemWatcher.stop()
			self.FileSystemWatcher = None

	def startFileSystemWatcher(self):
		try:
			if self.FileSystemWatcher and self.FileSystemWatcher.isRunning():
				return
			self.FileSystemWatcher = projectListener.FileSystemWatcher(self.filesChanged, self.callbackError, self.root_folder)
			self.FileSystemWatcher.start()

			return responseGenerator.createSuccessResponse("started FilesystemWatcher")
		except Exception as E:
			return responseGenerator.createExceptionResponse("could not start FilesystemWatcher")

	def checkIndex(self):
		json_project_structure = pathManager.path_to_dict(self.root_folder)
		if not json_project_structure:
			return responseGenerator.createExceptionResponse("no project structure found at: " + root_folder)

		if self.FileSystemWatcher and self.FileSystemWatcher.isRunning():
			self.FileSystemWatcher.pause()

		filesJson = multiPurposeParser.extractFiles(json_project_structure)

		try:
			#self.dropTables()
			self.databaseWrapper.createTables()
			dbFiles = self.databaseWrapper.selFiles()
			for dbFile in list(dbFiles):
				for file in list(filesJson):
					fullPath = file["path"]
					if dbFile.fullpath == fullPath:
						upToDate = file["lastmodified"] == dbFile.lastmodified
						if not upToDate:
							response = self.databaseWrapper.updateFile(file["path"],file["content"],file["lastmodified"],file["extension"])
							if response["status"] == "exception":
								return response
							#print("updated",file["path"])
							#print(models.Content.get(models.Content.filepath == dbFile.fullpath).headers)
						else:
							#print("file is up to date",file["path"])
							#print(models.Content.get(models.Content.filepath == dbFile.fullpath).headers)
							pass

						filesJson.remove(file)
						dbFiles.remove(dbFile)
						break
				

			#leftovers in db
			if dbFiles:
				for f in dbFiles:
					#print("deleting leftover",f.fullpath)
					response = self.databaseWrapper.deleteFile(f.fullpath)
					if response["status"] == "exception":
						return response

			if filesJson:
				for f in filesJson:
					#print("inserting new file",f["path"])
					response = self.databaseWrapper.insertFile(f["path"],f["content"],f["lastmodified"],f["extension"])
					if response["status"] == "exception":
						return response

			return responseGenerator.createSuccessResponse("indexed files")

		except Exception as E:
			return responseGenerator.createExceptionResponse("could not index files:" + str(E))
		finally:
			if self.FileSystemWatcher and self.FileSystemWatcher.isPaused():
				self.FileSystemWatcher.resume()


	def filesChanged(self,queueDict):
		if not self.databaseWrapper.tablesExist():
			return responseGenerator.createExceptionResponse("could not index: tables do not exist.. initialize db first")

		q = queueDict["queue"]
		filesChangedEvent = False
		updateWikipageEvent = False
		updatedPaths = []

		for entry in q:
			if not entry["valid"]:
				continue
			response = None
			if entry["type"] == "modified":
				response = self.databaseWrapper.updateFile(entry["srcPath"],entry["content"],entry["lastmodified"],pathManager.extensionNoDot(entry["srcPath"]))
				updatedPaths.append(entry["srcPath"])
				updateWikipageEvent = True

			elif entry["type"] == "created":
				response = self.databaseWrapper.insertFile(entry["srcPath"],entry["content"],entry["lastmodified"],pathManager.extensionNoDot(entry["srcPath"]))
				filesChangedEvent = True

			elif entry["type"] == "deleted":
				response = self.databaseWrapper.deleteFile(entry["srcPath"])
				filesChangedEvent = True

			elif entry["type"] == "moved":
				response = self.databaseWrapper.moveFile(entry["srcPath"],entry["destPath"],entry["lastmodified"])
				filesChangedEvent = True
			elif entry["type"] == "deletedDirectoryGuess":
				response = self.databaseWrapper.handleDeletedDirectoryGuess(entry["srcPath"])
				filesChangedEvent = True
			else:
				return responseGenerator.createExceptionResponse("files_changed event data is corrupted")

			if response["status"] == "exception":
				return response

		if filesChangedEvent:
			sessionManager.notifySubscribers("files_changed",self.sid)
		if updateWikipageEvent:
			for path in updatedPaths:
				sessionManager.notifySubscribers("update_wikipage",self.sid,path=path)

		self.wiki.send("files_changed",str(queueDict))
		return responseGenerator.createSuccessResponse("processed files_changed event")