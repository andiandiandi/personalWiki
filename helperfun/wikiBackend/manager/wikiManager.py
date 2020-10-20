from . import responseGenerator
from . import databaseManager
from . import pathManager
from . import searchQueryManager
from . import templateManager
from . import searchDataParser
from . import multiPurposeParser
from . import wordCount

import time
import json
import os
import re

import threading
from enum import Enum

urlRegex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class DbStatus(Enum):
	notConnected = 0
	connectionEstablished = 1
	projectInitialized = 2

class Wiki:
	def __init__(self,sid,socket):
		self.sid = sid
		self.socket = socket
		self.databaseWrapper = None
		self.indexer = None
		self.dbStatus = DbStatus.notConnected
		self.root_folder = None

	def callbackError(self,message):
		self.send("error",message)

	def send(self,event,strdata):
		self.socket.emit(event, strdata, room = self.sid)

	def cleanup(self):
		if self.indexer:
			self.indexer.cleanup()

			self.indexer = None
		if self.databaseWrapper:
			self.databaseWrapper.closeConnection()
			self.databaseWrapper = None

	def initializeProject(self, root_folder):
		if self.dbStatus == DbStatus.notConnected:
			response = pathManager.checkupWikiconfig(root_folder)
			if response["status"] == "exception":
				return response
			self.connectToDatabase(root_folder)

		if self.dbStatus.value >= DbStatus.connectionEstablished.value:
			self.indexer = databaseManager.Indexer(root_folder, self.sid, self.databaseWrapper, self.callbackError, self)
			response = self.indexer.initialize()
			if response["status"] == "exception":
				self.databaseWrapper.closeConnection()
				self.databaseWrapper = None
				self.indexer.cleanup()
				self.indexer = None
				
				return response

			self.root_folder = root_folder
			response = self.indexer.checkIndex()
			if response["status"] == "exception":
				return response

			self.dbStatus = DbStatus.projectInitialized

			return responseGenerator.createSuccessResponse("project initialized")

		return responseGenerator.createExceptionResponse("could not initialize project")

	def connectToDatabase(self,root_folder):
		self.databaseWrapper = databaseManager.DatabaseWrapper(root_folder, self.sid, self.callbackError)
		dbConnectionEstablished = self.databaseWrapper.create_connection()
		
		if dbConnectionEstablished:
			self.dbStatus = DbStatus.connectionEstablished
			return responseGenerator.createSuccessResponse("connected to Database")

		return responseGenerator.createExceptionResponse("could not connect to Database")

	def send(self,event,jsondata):
		self.socket.emit(event,jsondata,room=self.sid)

	def runRealSearchQuery(self,queryString):
		response = searchQueryManager.parseQuery(queryString)
		if response["status"] == "exception":
			return response
		elif response["status"] == "success":
			parsedQueryD = json.loads(response["response"])
			if "searchhistory" in parsedQueryD and parsedQueryD["searchhistory"]:
				self.databaseWrapper.addSearchQuery(parsedQueryD["searchhistory"])				
			if parsedQueryD["type"] == "delete":
				return self.deleteSavedQuery(parsedQueryD["query"])
			if parsedQueryD["type"] == "tagsearch":
				jsondataTagQuery = searchQueryManager.jsondataTagQuery(parsedQueryD["phrase"],parsedQueryD["args"])
				return self.runSearchQuery(jsondataTagQuery)
			elif parsedQueryD["type"] == "fulltextsearch":
				jsondataFulltextQuery = searchQueryManager.jsondataFulltextQuery(parsedQueryD["phrase"],parsedQueryD["args"])
				return self.searchFulltext(jsondataFulltextQuery)
		else:
			return response

	def clearDatabase(self):
		return self.databaseWrapper.clearDatabase()

	def deleteSavedQuery(self,queryString):
		return self.databaseWrapper.deleteSavedQuery(queryString)

	def wordCount(self, path = None):
		try:
			if path:
				file = self.databaseWrapper.getFile(path)
				if file:
					content = self.databaseWrapper.getContent(file.id)
					if content:
						textString = content.rawString
						wordsChars = wordCount.countWordsCharReadtime(textString)		
						return wordsChars

					return responseGenerator.createExceptionResponse("Could not find content for wordCount: " + path)
				return responseGenerator.createExceptionResponse("Could not find file for wordCount: " + path)

			else:
					wordsCharsReadtimeList = self.databaseWrapper.selWordsCharsReadtime()
					if type(wordsCharsReadtimeList) == dict and "status" in wordsCharsReadtimeList:
						return wordsCharsReadtimeList

					words = 0
					chars = 0
					readtimeInSeconds = 0
					for wordsCharsReadtime in wordsCharsReadtimeList:
						words += wordsCharsReadtime["words"]
						chars += wordsCharsReadtime["chars"]
						readtimeInSeconds += wordsCharsReadtime["readtimeInSeconds"]

					return {"words":words,"chars":chars,"readtimeInSeconds":readtimeInSeconds}
						
		except Exception as E:
			return responseGenerator.createExceptionResponse("could not count words,chars,readtime: " + (path if path else "query on whole notebook") + " | " + str(E) + " | " + type(E).__name__)

	def generateWikilinkData(self,filename,srcPath):
			def listFiles(fullpathList):
				l = []
				for fullpath in fullpathList:
					d = {"title":filename,"link":os.path.relpath(fullpath,os.path.dirname(srcPath)),"tooltip":fullpath}
					l.append(d)		
				return l

			fullpathList = self.databaseWrapper.selFullpathFromFile(filename)
			if type(fullpathList) == dict and "status" in fullpathList:
				return fullpathList

			l = listFiles(fullpathList)
			d = {}
			if l:
				d["type"] = "directlink"
				d["files"] = l		
			if not l:
				d["type"] = "create"
				d["filename"] = filename
				templatePathDict = templateManager.templatePathDict()
				d["templates"] = list(templatePathDict.keys()) if templatePathDict else []
				d["folders"] = pathManager.listFolders(self.root_folder)

			return responseGenerator.createSuccessResponse(d)

	def generateImagelinkData(self,srcPath):
		with self.db.bind_ctx(models.modellist):
			fullpathsList = self.databaseWrapper.selAllFullpathFromImage()
			if type(fullpathList) == dict and "status" in fullpathList:
				return fullpathList

			for fullpath in fullpathsList:
				l.append({"title":"","link":os.path.relpath(fullpath,os.path.dirname(srcPath)),"tooltip":fullpath})

			d = {}
			if l:
				d["type"] = "directimagelink"
				d["files"] = l		
			if not l:
				d["type"] = "createimagelink"

			return responseGenerator.createSuccessResponse(d)


	def createWikilink(self,template,folder,filename,srcPath):
		if folder.startswith(self.root_folder):
			if not pathManager.exists(folder):
				response = pathManager.createFolder(folder)
				if response["status"] == "exception":
					return response

			realFilename = os.path.join(folder,filename + ".md")
			response = None
			if template:
				templateContent = templateManager.getContent(template,filename)
				response = pathManager.dump(templateContent if templateContent else "",realFilename)
			else:
				response = pathManager.dump("",realFilename)
			if response["status"] == "exception":
				return response

			d = {}
			d["type"] = "directlink"
			d["files"] = [{"title":filename,"link":os.path.relpath(realFilename,os.path.dirname(srcPath)),"tooltip":realFilename}]

			return responseGenerator.createSuccessResponse(d)

		else:
			return responseGenerator.createExceptionResponse("could not create Wikilink: " + filename + " | " + "folder not in notebook")

	def searchFulltext(self,jsondataFulltextQuery):
		files = jsondataFulltextQuery["files"]
		files_exclude = jsondataFulltextQuery["files_exclude"]
		span = jsondataFulltextQuery["span"]
		phrase = jsondataFulltextQuery["phrase"]
		query = None
		toret = {"type":"fulltextsearch"}
		query = self.databaseWrapper.selFulltextsearchMetadata(files_exclude,files)

		if type(query) == dict and "status" in query:
			return query

		result = []
		for entry in query:
			wordhash = entry["wordhash"]
			fullpath = entry["fullpath"]
			try:
				wordhashD = json.loads(wordhash)
				findingsD = multiPurposeParser.search(phrase,wordhashD,linespan=span,filepath=fullpath)
				if findingsD:
					result += findingsD
			except Exception as E:
				return responseGenerator.createExceptionResponse("fulltext-search across whole notebook failed: " + " | " + str(E) + " | " + str(type(E).__name__))

		result = sorted(result, key=lambda k: k['rating'], reverse=True)
		toret["data"] = result
		return responseGenerator.createSuccessResponse(toret)


	def wikipageHtml(self,path):
		try:
			file = self.databaseWrapper.getFile(path)
			if file:
				content = self.databaseWrapper.getContent(file.id)
				if content:
					base64PathDict = {}
					wikilinks = content.textlinks	
					imagelinks = json.loads(content.imagelinks)
					if imagelinks:
						dirname = os.path.dirname(path)
						l = {}
						for entry in imagelinks:
							relpath = entry["src"]
							if not re.match(urlRegex,relpath):
								if relpath.startswith("/"):
									relpath = relpath[1:]
								l[os.path.normpath(os.path.join(dirname,relpath))] = relpath


						def DataUriGraphic(base64String,mimetype):
							return "data:image/{0};base64,{1}".format(mimetype,base64String)

						if l:
							imageDataList = self.databaseWrapper.selImageData(list(l.keys()))

							if type(imageDataList) == dict and "status" in imageDataList:
								return imageDataList

							for entry in imageDataList:
								relpath = l[entry["fullpath"]]
								base64PathDict[relpath] = DataUriGraphic(entry["base64"],entry["mimetype"])

					html = multiPurposeParser.md2html(content.rawString, path, wikilinks = content.textlinks, base64PathDict = base64PathDict)
					return html
				else:
					return "CONTENT OF WIKIPAGE NOT FOUND IN DATABASE"
		except Exception as E:
			return "Exception while generating wikipage: " + str(E) + " | " + type(E).__name__


	def listSearchQuery(self,root_folder):
		return self.databaseWrapper.listSearchQuery(root_folder)

	def runSearchQuery(self,jsondata):
		if "files" in jsondata and "element" in jsondata and "values" in jsondata:
			files = jsondata["files"]
			element = jsondata["element"]
			values = jsondata["values"]
			try:
				toret = {"type":"tagsearch"}
				result = searchDataParser.search(files,element,values,self.databaseWrapper.db)
				#elementHandlers[element["value"]](files,element,values,self.db)
				toret["data"] = result
				return responseGenerator.createSuccessResponse(toret)
			except Exception as E:
				return responseGenerator.createExceptionResponse("could not run tag-searchQuery: " + str(E) + " | " + type(E).__name__)
		else:
			return responseGenerator.createExceptionResponse("could not run tag-searchQuery: " + '"files" or "values" key not existent')