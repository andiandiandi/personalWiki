import os
from .libs.peewee.peewee import *
from .libs.peewee.playhouse import *
from .libs.peewee.playhouse.sqlite_ext import *
from . import models

import json
import time

import threading
from threading import Lock

from . import searchDataParser
from . import responseGenerator

from .libs import mistletoe
from .libs.mistletoe.ast_renderer import ASTRenderer
from . import sessionManager
from . import pathManager
from .pathManager import Filetype
from . import wordCount

from . import searchQueryManager

from . import templateManager

from fuzzywuzzy import fuzz

import itertools
from collections import Counter

urlRegex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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


def textDict(md_ast):
	l = []
	if "children" in md_ast:
		for entry in md_ast["children"]:
			l += textDict(entry)
	elif "content" in md_ast:
			content = re.sub('\W+',' ', md_ast["content"]).strip()
			if content:
				l.append({"start":md_ast["span"]["start"],"read":md_ast["span"]["read"],"content": content})
	return l



def createWordHash(textDict):
	d = {}
	d["lines"] = {}
	for entry in textDict:
		content = entry["content"]
		d["lines"][entry["start"]] = content
		for word in content.split(" "):
			if word:
				if word[:1] not in d:
					d.setdefault(word[:1],[]).append((word,list(set([entry["start"]]))))
				else:
					#(word,[start,..])
					found = False
					for e in d[word[:1]]:
						if e[0] == word:
							e[1].append(entry["start"])
							found = True
							break
					if not found:
						d[word[:1]].append((word,list(set([entry["start"]]))))

	return d


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

def search(phrase, wordHash, linespan=0,filepath = None):
	def validLines(tupl):
		for t in tupl:
			found = True
			for x in tupl:
				if t == x:
					continue
				else:
					if not abs(t-x) <= int(linespan):
						found = False
						break;
			if found:
				return True

		return False

	def lines(l):

		result = set()
		if len(l) > 1:
			for e in itertools.product(*l):
				validTuple = validLines(e)
				if validTuple:
					sortedUniqueLines = tuple(sorted(set(e)))
					if len(sortedUniqueLines) > 2:
						sortedUniqueLines = (sortedUniqueLines[0],sortedUniqueLines[-1])
					result.add(sortedUniqueLines)
			return list(result)
		else:
			entry = l[0]
			return [tuple([i]) for i in entry]

	def findWord(searchword,wordlist):
		bestratio = -1
		bestmatch = None
		for wordLineTuple in wordlist:
			#word
			w = wordLineTuple[0]
			#here compare
			ratio = fuzz.ratio(w.lower(),searchword.lower())
			if ratio >= 85 and ratio > bestratio:
				bestmatch = wordLineTuple[1]

		return bestmatch

	finalResult = None
	#["hallo ich","auto meer"]
	combinations = []
	#["hallo ich"]
	abort = False
	if not type(phrase) == list:
		phrase = [w.replace(" ","") for w in phrase.split(" ")]
	for word in phrase:
		#[(word,[start])]
		if not word[:1] in wordHash:
			return None
		wordlist = wordHash[word[:1]]
		#(word,[start])
		listOfLines = findWord(word,wordlist)
		if listOfLines:			
			combinations.append(listOfLines)
		else:
			abort = True
			break;

	if abort:
		return None
	else:
		result = lines(combinations)
		l = []
		for i in result:
			a = Counter(i).most_common(1)[0]
			fullphrase = "PREVIEW NOT AVAILABLE"
			try:
				fullphrase = "...".join([wordHash["lines"][str(line)] for line in i])
			except:
				pass
			r = {"lines":i,"rating":round(i[0]/(sum(i)/len(i)),2),"fullphrase":fullphrase}
			if filepath:
				r["filepath"] = filepath
			l.append(r)
		if l:
			sortedFindings = sorted(l, key=lambda k: k['rating'], reverse=True) 
			finalResult = sortedFindings

	return finalResult


def parseContentMistletoe(content):
	tree = mistletoe.markdown(content, ASTRenderer)
	#print(tree)
	return tree

def md2html(content,path,wikilinks=None,base64PathDict = None):
	try:
		tree = mistletoe.markdown(content,path=path,wikilinks=wikilinks,base64PathDict=base64PathDict)
		return tree
	except Exception as e:
		return str(e)

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
		self.modeldict["image"] = models.Image
		self.modeldict["searchquery"] = models.SearchQuery

		self.lock = Lock()

	def create_connection(self):
		try:
			self.db = SqliteExtDatabase(os.path.join(self.wiki.root_folder,"wikiconfig","wiki.db"))
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

	def runRealSearchQuery(self,queryString):
		response = searchQueryManager.parseQuery(queryString)
		if response["status"] == "exception":
			return response
		elif response["status"] == "success":
			parsedQueryD = json.loads(response["response"])
			if "searchhistory" in parsedQueryD and parsedQueryD["searchhistory"]:
				self.addSearchQuery(parsedQueryD["searchhistory"])				
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


	def wordCount(self, path = None):
		try:
			if path:
				file = self.getFile(path)
				if file:
					content = self.getContent(file.id)
					if content:
						textString = content.rawString
						wordsChars = wordCount.countWordsCharReadtime(textString)		
						return wordsChars

					return responseGenerator.createExceptionResponse("Could not find content for wordCount: " + path)
				return responseGenerator.createExceptionResponse("Could not find file for wordCount: " + path)

			else:
				with self.db.bind_ctx(models.modellist):
					query = models.File.select(models.Content.wordsCharsReadtime).join(models.Content)
					words = 0
					chars = 0
					readtimeInSeconds = 0
					for row in query:
						wordsCharsReadtime = json.loads(row.content.wordsCharsReadtime)
						words += wordsCharsReadtime["words"]
						chars += wordsCharsReadtime["chars"]
						readtimeInSeconds += wordsCharsReadtime["readtimeInSeconds"]

					return {"words":words,"chars":chars,"readtimeInSeconds":readtimeInSeconds}
						
		except Exception as E:
			return responseGenerator.createExceptionResponse("could not count words,chars,readtime: " + (path if path else "query on whole notebook") + " | " + str(E) + " | " + type(E).__name__)

	def generateWikilinkData(self,filename,srcPath):
		with self.db.bind_ctx(models.modellist):

			def listFiles(fileQuery):
				l = []
				for file in fileQuery:
					d = {"title":filename,"link":os.path.relpath(file.fullpath,os.path.dirname(srcPath)),"tooltip":file.fullpath}
					l.append(d)		
				return l

			fileQuery = models.File.select(models.File.fullpath).where(models.File.name == filename)
			l = listFiles(fileQuery)
			d = {}
			if l:
				d["type"] = "directlink"
				d["files"] = l		
			if not l:
				d["type"] = "create"
				d["filename"] = filename
				templatePathDict = templateManager.templatePathDict()
				d["templates"] = list(templatePathDict.keys()) if templatePathDict else []
				d["folders"] = pathManager.listFolders(self.wiki.root_folder)

			return responseGenerator.createSuccessResponse(d)

	def createWikilink(self,template,folder,filename,srcPath):
		if folder.startswith(self.wiki.root_folder):
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

	def generateImagelinkData(self,srcPath):
		with self.db.bind_ctx(models.modellist):
			imageQuery = models.File.select(models.File.fullpath).join(models.Image).where(models.File.id==models.Image.fileid)
			l = []
			for file in imageQuery:
				l.append({"title":"","link":os.path.relpath(file.fullpath,os.path.dirname(srcPath)),"tooltip":file.fullpath})

			d = {}
			if l:
				d["type"] = "directimagelink"
				d["files"] = l		
			if not l:
				d["type"] = "createimagelink"

			return responseGenerator.createSuccessResponse(d)

	def checkIndex(self):
		json_project_structure = pathManager.path_to_dict(self.wiki.root_folder)
		if not json_project_structure:
			return false

		filesJson = extractFiles(json_project_structure)

		try:
			#self.dropTables()
			self.createTables()
			dbFiles = self.selFiles()
			for dbFile in list(dbFiles):
				for file in list(filesJson):
					fullPath = file["path"]
					if dbFile.fullpath == fullPath:
						upToDate = file["lastmodified"] == dbFile.lastmodified
						if not upToDate:
							response = self.updateFile(file["path"],file["content"],file["lastmodified"],file["extension"])
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
					response = self.deleteFile(f.fullpath)
					if response["status"] == "exception":
						return response

			if filesJson:
				for f in filesJson:
					print("inserting new file",f["path"])
					response = self.insertFile(f["path"],f["content"],f["lastmodified"],f["extension"])
					if response["status"] == "exception":
						return response

			return responseGenerator.createSuccessResponse("indexed files")

		except Exception as E:
			return responseGenerator.createExceptionResponse("could not index files:" + str(E))

	def deleteFile(self,fullpath):
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


	def filesChanged(self,queueDict):
		with self.lock:
			q = queueDict["queue"]
			filesChangedEvent = False
			updateWikipageEvent = False
			updatedPaths = []

			for entry in q:
				if not entry["valid"]:
					continue
				response = None
				if entry["type"] == "modified":
					response = self.updateFile(entry["srcPath"],entry["content"],entry["lastmodified"],pathManager.extensionNoDot(entry["srcPath"]))
					updatedPaths.append(entry["srcPath"])
					updateWikipageEvent = True

				elif entry["type"] == "created":
					response = self.insertFile(entry["srcPath"],entry["content"],entry["lastmodified"],pathManager.extensionNoDot(entry["srcPath"]))
					filesChangedEvent = True

				elif entry["type"] == "deleted":
					response = self.deleteFile(entry["srcPath"])
					filesChangedEvent = True

				elif entry["type"] == "moved":
					response = self.moveFile(entry["srcPath"],entry["destPath"],entry["lastmodified"])
					filesChangedEvent = True
				else:
					return responseGenerator.createExceptionResponse("files_changed event data is corrupted")

				if response["status"] == "exception":
					return response

			if filesChangedEvent:
				sessionManager.notifySubscribers("files_changed",self.wiki.sid)
			if updateWikipageEvent:
				for path in updatedPaths:
					sessionManager.notifySubscribers("update_wikipage",self.wiki.sid,path=path)

			return responseGenerator.createSuccessResponse("processed files_changed event")

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
					
					sessionManager.notifySubscribers("rename_wikipage",self.wiki.sid,path=srcPath,jsondata=destPath)
					if response["status"] == "exception":
						return response


				return responseGenerator.createSuccessResponse("moved file: " + json.dumps({"srcpath":srcPath,"destpath":destPath,"lastmodified":lastmodified}))


			except Exception as E:
				return responseGenerator.createExceptionResponse("could not move file: " + srcPath + " to " + destPath + " | " + str(E))

	def fileRenamedTrigger(self,srcPath,destPath,mimetype):
		with self.db.bind_ctx(models.modellist):
			try:
				if pathManager.filetype(mimetype) == Filetype.wikipage:
					#query = (models.Content.select(models.Content.textlinks,models.Content.fileid,models.Content.rawString).join(models.File).where(models.Content.hasWikilink(srcPath,models.File.fullpath)))
					l = []
					pathContentL = {}
					query = (models.File.select(models.Content.textlinks,models.Content.rawString,models.File.fullpath).join(models.Content))
					for file in query:
						try:
							d = json.loads(file.content.textlinks)
							l.append((srcPath,file.fullpath,d,file.content.rawString))
						except:
							continue
					for item in l:
						hasWikilink = models.Content.hasWikilink(item[0],item[1],item[2])						
						if hasWikilink:
							pathContentL[item[1]] = item[3]

					replacee = pathManager.basename_w_ext_of_path(srcPath)
					toreplace = pathManager.basename_w_ext_of_path(destPath)
					for path, rawContent in pathContentL.items():
						pathContentL[path] = rawContent.replace(replacee,toreplace)

					print(pathContentL)
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
				tree = parseContentMistletoe(content)
				dictTree = json.loads(tree)
				#textdict = json.dumps(parseText(tree))
				imagelinks = json.dumps(list_of_imagelinks(dictTree))
				textlinks = json.dumps(list_of_textlinks(dictTree))
				textdict = ""
				headers = json.dumps(list_of_headers(dictTree))
				footnotes = json.dumps(list_of_footnotes(dictTree))
				wordsCharsReadtime = json.dumps(wordCount.countWordsCharReadtime(content))
				w = createWordHash(textDict(dictTree))
				print("w",w)
				wordhash = json.dumps(w)
				print("update wordhash",wordhash)
				contentupdateQuery = models.Content.update(wordhash=wordhash, textdict = textdict, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes, rawString = content, wordsCharsReadtime=wordsCharsReadtime).where(models.Content.fileid == fileid)
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
				tree = parseContentMistletoe(content)
				dictTree = json.loads(tree)
				#textdict = json.dumps(parseText(tree))
				imagelinks = json.dumps(list_of_imagelinks(dictTree))
				textlinks = json.dumps(list_of_textlinks(dictTree))
				textdict = ""
				headers = json.dumps(list_of_headers(dictTree))
				footnotes = json.dumps(list_of_footnotes(dictTree))
				wordsCharsReadtime = json.dumps(wordCount.countWordsCharReadtime(content))
				w = createWordHash(textDict(dictTree))
				print("w",w)
				wordhash = json.dumps(w)
				print("insert wordhash",wordhash)
				c = self.modeldict["content"].create(wordhash=wordhash,textdict = textdict, textlinks = textlinks,imagelinks = imagelinks,headers = headers, footnotes = footnotes, rawString = content,wordsCharsReadtime=wordsCharsReadtime,fileid=fileid)

				return responseGenerator.createSuccessResponse("inserted wikipage:" + str(fileid))

			except Exception as E:
				return responseGenerator.createExceptionResponse("exception while inserting wikipage: " + str(E))
				
	def searchFulltext(self,jsondataFulltextQuery):
	#def searchFulltext(self,phrase,linespan=0,filepath=None):
		with self.db.bind_ctx(models.modellist):
			files = jsondataFulltextQuery["files"]
			files_exclude = jsondataFulltextQuery["files_exclude"]
			span = jsondataFulltextQuery["span"]
			phrase = jsondataFulltextQuery["phrase"]
			print(jsondataFulltextQuery)
			query = None
			toret = {"type":"fulltextsearch"}
			if files_exclude:
				query = models.File.select(models.File.fullpath,models.Content.wordhash).join(models.Content).where(~models.File.fileIn(files))
			else:
				if files:
					query = models.File.select(models.File.fullpath,models.Content.wordhash).join(models.Content).where(models.File.fileIn(files))
				else:
					query = models.File.select(models.File.fullpath,models.Content.wordhash).join(models.Content)
			result = []
			for row in query:
				wordhash = row.content.wordhash
				try:
					wordhashD = json.loads(wordhash)
					findingsD = search(phrase,wordhashD,linespan=span,filepath=row.fullpath)
					if findingsD:
						result += findingsD
				except Exception as E:
					return responseGenerator.createExceptionResponse("fulltext-search across whole notebook failed: " + " | " + str(E) + " | " + str(type(E).__name__))

			result = sorted(result, key=lambda k: k['rating'], reverse=True)
			toret["data"] = result
			return responseGenerator.createSuccessResponse(toret)

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

	def initializeProject(self,json):
		with self.db.bind_ctx(models.modellist):
			initProject(self.db,self.modeldict,json)

	def wikipageHtml(self,path):
		with self.db.bind_ctx(models.modellist):
			try:
				file = self.getFile(path)
				if file:
					content = models.Content.get_or_none(models.Content.fileid == file.id)
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
								query = (models.File.select(models.File.fullpath,models.Image.base64,models.Image.mimetype).join(models.Image).where(models.File.fullpath.in_(list(l.keys()))))
								for row in query:
									relpath = l[row.fullpath]
									base64PathDict[relpath] = DataUriGraphic(row.image.base64,row.image.mimetype)

						html = md2html(content.rawString, path, wikilinks = content.textlinks, base64PathDict = base64PathDict)
						return html
					else:
						return "CONTENT OF WIKIPAGE NOT FOUND IN DATABASE"
			except Exception as E:
				return "Exception while generating wikipage: " + str(E) + " | " + type(E).__name__

	def selContent(self):
		with self.db.bind_ctx(models.modellist):
			try:
				r = models.Content.select()
				l = []
				for f in r:	
					l.append(f.fileid)
					l.append(f.headers)
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
				#print("folderid:",f.folderid)
				#print("___________________________")
				l.append(f)
			return l

	def getFile(self,fullPath):
		with self.db.bind_ctx(models.modellist):
			file = models.File.get_or_none(models.File.fullpath == fullPath)
			if file:
				return file
			return None

	def getContent(self,fileid):
		with self.db.bind_ctx(models.modellist):
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


	def listSearchQuery(self):
		with self.db.bind_ctx(models.modellist):
			try:
				searchQuery = models.SearchQuery.select()
				l = []
				for row in searchQuery:
					l.append({"rawString":row.rawString,"creationdate":row.creationdate})
				return responseGenerator.createSuccessResponse(l)
			except Exception as E:
				return responseGenerator.createExceptionResponse("could not list search queries: " + str(E) + " | " + type(E).__name__)

	def addSearchQuery(self,queryString):
		with self.db.bind_ctx(models.modellist):
			c = self.modeldict["searchquery"].create(rawString = queryString,creationdate = int(round(time.time() * 1000)))


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
			persisted_file = self.modeldict["file"].create(fullpath = fullpath, lastmodified = lastmodified)

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
		if "files" in jsondata and "element" in jsondata and "values" in jsondata:
			files = jsondata["files"]
			element = jsondata["element"]
			values = jsondata["values"]
			try:
				toret = {"type":"tagsearch"}
				result = searchDataParser.search(files,element,values,self.db)
				#elementHandlers[element["value"]](files,element,values,self.db)
				toret["data"] = result
				return responseGenerator.createSuccessResponse(toret)
			except Exception as E:
				return responseGenerator.createExceptionResponse("could not run tag-searchQuery: " + str(E) + " | " + type(E).__name__)
		else:
			return responseGenerator.createExceptionResponse("could not run tag-searchQuery: " + '"files" or "values" key not existent')