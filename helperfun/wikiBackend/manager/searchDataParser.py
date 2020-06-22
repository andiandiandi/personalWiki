import json
from . import models
from .libs.peewee.peewee import Expression
import os
import re

def headerHandler(files,rootelement,rootvalues,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("headers",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.path)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			return parseQuery(query,rootelement,rootvalues)



def footnoteHandler(files,rootelement,values,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("footnotes",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.path)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			parseQuery(query,rootelement,rootvalues)


def imagelinkHandler(files,rootelement,values,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("imagelinks",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.path)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			parseQuery(query,rootelement,rootvalues)


def textlinkHandler(files,rootelement,rootvalues,db):
	elemn = extn(rootelement)
	if elemn:
		return fetch_without_element("textlinks",db)
	else:
		filesv = extv(files)
		filesn = extn(files)
		with db.bind_ctx(models.modellist):
			query = (models.File.select(elementmapping[rootelement["value"]],models.File.name,models.File.extension,models.File.path)
										.join(models.Content).where(models.File.name.concat(models.File.extension).in_(filesv)))
			return parseQuery(query,rootelement,rootvalues)


def parseQuery(query,rootelement,rootvalues):
	toret = []
	for row in query:
		jsonstr = getattr(row.content,rootelement["value"])
		parsed = json.loads(jsonstr)
		print("parsed",parsed)
		if parsed:
			retobj = createFile(row.name,row.extension,row.path)
			for element in parsed:
				print("ele",element)
				fulfilled = True
				for value in rootvalues:
					print("value",value)
					print("element",element)
					attribute = value["attribute"]
					attribute_value = value["value"]
					negate = value["negate"]
					child = None
					if attribute in element:
						if not (re.compile(attribute_value).match(child[attribute]) if negate else re.compile(attribute_value).match(child[attribute])):
							fulfilled = False
							break
					else:
						if "children" in element:
							child = element["children"][0]
							if attribute in child:
								if not (re.compile(attribute_value).match(child[attribute]) if negate else re.compile(attribute_value).match(child[attribute])):
									fulfilled = False
									break
				if fulfilled:
					retobj["span"].append(element["span"])
			toret.append(retobj)
										

		return toret

def fetch_without_element(elementname,db):
	tofetch = elementmapping[elementname]
	if tofetch:
		with db.bind_ctx(models.modellist):
			query = (models.File.select(tofetch, models.File.name,models.File.extension,models.File.path)
						.join(models.Content))
			toret = []
			for row in query:
				content = getattr(row,"content")
				element = getattr(content,elementname)
				d = json.loads(element)
				if not d:
					toret.append(createRet(row.name,row.extension,row.path,None))
			return toret

def createFile(name,extension,path):
	return {"file":{"name":name,"extension":extension,"path":path},"span":[]}

def createRet(name,extension,path,span):
	return {"file":{"name":name,"extension":extension,"path":path},"span":span}

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