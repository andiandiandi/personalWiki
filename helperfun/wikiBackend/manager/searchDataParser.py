import json
from . import models
from .libs.peewee.peewee import Expression
import os
import re

#query: {"files":{"negate":False,"values":["newfile.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header2"}]}
"""header
content
level

"""


def headerHandler(files,rootelement,rootvalues,db):
	elemn = extn(rootelement)
	filesv = extv(files)
	filesn = extn(files)

	if elemn:
		return fetch_without_element("headers",filesv,filesn,db)
	else:	
		with db.bind_ctx(models.modellist):
			#elementmapping {'headers': <CharField: Content.headers>, 'footnotes': <CharField: Content.footnotes>, 'textlinks': <CharField: Content.textlinks>, 'imagelinks': <CharField: Content.imagelinks>}
			#rootelement {'negate': False, 'value': 'headers'}
			#basename_w_ext = models.File.fullpath.
			query = None
			if filesn:
				if filesv:
					query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content).where(~models.File.fileIn(filesv)))
				else:
					query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content))
			else:
				if filesv:
					query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content).where(models.File.fileIn(filesv)))

					#query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
					#					.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
				else:
					query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content))
			for x in query:
				print(x.name)

			if query:
				return parseQuery(query,rootelement,rootvalues)

			return None




def footnoteHandler(files,rootelement,values,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("footnotes",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			return parseQuery(query,rootelement,rootvalues)


def imagelinkHandler(files,rootelement,values,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("imagelinks",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			return parseQuery(query,rootelement,rootvalues)


def textlinkHandler(files,rootelement,rootvalues,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("textlinks",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.relpath)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			return parseQuery(query,rootelement,rootvalues)

#query: {"files":{"negate":False,"values":["newfile.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header2"}]}
"""header
content
level

"""

def parseQuery(query,rootelement,rootvalues):
	debug = False
	toret = []
	for file in query:
		jsonstr = getattr(file.content,rootelement["value"])
		parsed = json.loads(jsonstr)
		if debug:
			print("parsed",parsed)
		if parsed:
			for element in parsed:
				if debug:
					print("ele",element)
				fulfilled = True
				for value in rootvalues:
					if debug:
						print("value",value)
						print("element",element)
						print("attribute",value["attribute"])
						print("attribute_value", value["value"])
					attribute = value["attribute"]
					attribute_value = value["value"]
					negate = value["negate"]
					child = None
					if attribute in element:
						if negate:
							if (re.compile(attribute_value).match(str(element[attribute]))):
								fulfilled = False
								break
						else:
							if debug:
								print("element[attribute]",element[attribute])
							if not re.compile(attribute_value).match(str(element[attribute])):
								fulfilled = False
								break
					else:
						if "children" in element:
							child = element["children"][0]
							if attribute in child:
								if negate:
									if (re.compile(attribute_value).match(str(child[attribute]))):
										fulfilled = False
										break
								else:
									if debug:
										print("element[attribute]",child[attribute])
									if not re.compile(attribute_value).match(str(child[attribute])):
										fulfilled = False
										break
				if fulfilled:
					retobj = createFile(file.name,file.extension,file.relpath)
					retobj["span"].append(element["span"])
					toret.append(retobj)
										
	if toret:
		return toret
	return None

def fetch_without_element(elementname,filesv,filesn,db):
	tofetch = elementmapping[elementname]
	if tofetch:
		with db.bind_ctx(models.modellist):
			if filesn:
				if filesv:
					query = (models.File.select(tofetch,models.File.name,models.File.extension,models.File.relpath)
							.join(models.Content).where(~models.File.fileIn(filesv)))
										
				else:
					query = (models.File.select(tofetch,models.File.name,models.File.extension,models.File.relpath)
							.join(models.Content))

			else:
				if filesv:
					query = (models.File.select(tofetch,models.File.name,models.File.extension,models.File.relpath)
							.join(models.Content).where(models.File.fileIn(filesv)))

				else:
					query = (models.File.select(tofetch,models.File.name,models.File.extension,models.File.relpath)
							.join(models.Content))
			toret = []
			for file in query:
				contentColumn = getattr(file.content,elementname)
				try:
					contentColumnJSON = json.loads(contentColumn)
					if not contentColumnJSON:
						toret.append(createRet(file.name,file.extension,file.relpath,None))

				except Exception as E:
					print("exp in fetchWithoutElement:" + str(E))
					continue
			if toret:
				return toret
			return None

def createFile(name,extension,relpath):
	return {"file":{"name":name,"extension":extension,"path":relpath},"span":[]}

def createRet(name,extension,relpath,span):
	return {"file":{"name":name,"extension":extension,"path":relpath},"span":span}

def extv(obj):
	if "values" in obj:
		return obj["values"]
	else:
		raise Exception("Key 'values' not found") 

def extn(obj):
	if "negate" in obj:
		return obj["negate"]
	else:
		raise Exception("Key 'negate' not found") 

elementHandlers = {"headers": headerHandler,
				   "footnotes": footnoteHandler,
				   "imagelinks": imagelinkHandler,
				   "textlinks": textlinkHandler,}
elementmapping = {"headers":models.Content.headers,
				  "footnotes": models.Content.footnotes,
				  "textlinks": models.Content.textlinks,
				  "imagelinks": models.Content.imagelinks}


