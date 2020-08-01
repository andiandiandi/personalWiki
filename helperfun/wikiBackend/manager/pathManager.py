import base64
import os
from enum import Enum
import io

from . import responseGenerator

def basename_w_ext_of_path(full_filepath_with_name):
	temp = os.path.splitext(os.path.basename(full_filepath_with_name))
	return temp[0] + temp[1]

def extension_of_filepath(full_filepath_with_name):
	return os.path.splitext(os.path.basename(full_filepath_with_name))[1]

def listFolders(root_folder):
	return [x[0] for x in os.walk(root_folder) if os.path.basename(x[0]) != "wikiconfig"]

def folder_has_file(folder,full_path_of_file):
	for folder, subs, files in os.walk(folder):
			for filename in files:
				if(filename == os.path.basename(full_path_of_file)):
					return True

def createFolder(foldername):
	try:
		os.makedirs(foldername)
	except FileExistsError:
		return responseGenerator.createExceptionResponse("folder exists")
	except Exception as E:
		return responseGenerator.createExceptionResponse("could not create folder: " + foldername + " | " + str(E) + " | " + type(E).__name__)

def dump(strContent,wherePath):
	try:
		with open(wherePath, 'w+') as file:
			file.write(strContent)
		return responseGenerator.createSuccessResponse("dumped content")
	except Exception as E:
		return responseGenerator.createExceptionResponse("could not dump to file: " + wherePath + " | " + str(E) + " | " + type(E).__name__)


def path_to_helperfun():
	return os.path.dirname(__file__)

def exists(full_path_of_file):
	return os.path.exists(full_path_of_file) 

def resolve_relative_path(base_path,relative_navigation):
	unresolved_rel_path = os.path.join(base_path, relative_navigation)
	#points to root-folder of this plugin
	resolved_abs_path = os.path.realpath(unresolved_rel_path)

	return resolved_abs_path

def writeFiles(pathContentDict):
	for path, content in pathContentDict.items():
		try:
			with io.open(path, 'w', encoding = 'utf-8') as file:
				file.write(content)
		except Exception as E:
			print("EX" + str(E) + "<" + type(E).__name__)
			continue

def filename(path):
	base = os.path.basename(path)
	return os.path.splitext(base)[0]
		
def extension(path):
	base = os.path.basename(path)
	return os.path.splitext(base)[1]

def relpath(path):
	return os.path.dirname(path)

def extensionNoDot(path):
	base = os.path.basename(path)
	ext = os.path.splitext(base)[1]
	return ext[1:]

def path_to_plugin_folder():
	return resolve_relative_path(path_to_helperfun(),"..")

def supportedExtensions():
	return [".md",".jpg",".jpeg",".png",".gif"]

class Filetype(Enum):
	wikipage = 0
	image = 1


def filetype(extension):
	if extension == "md":
		return Filetype.wikipage
	elif extension in ["jpg","jpeg","png","gif"]:
		return Filetype.image
	else:
		return None

def generateFileData(full_path):
	broken = False
	d = {}
	d["path"] = full_path
	d["extension"] = extensionNoDot(full_path)


	if filetype(d["extension"]) == Filetype.wikipage:
		d["content"] = open(full_path, 'r', encoding='utf8').read()
	elif filetype(d["extension"]) == Filetype.image:
		with open(full_path, "rb") as imageFile:
			strContent = base64.b64encode(imageFile.read())
			d["content"] = strContent
	else:
		broken = True

	d["lastmodified"] = os.path.getmtime(full_path)
	if broken:
		d["content"] = "BROKEN CONTENT"

	return d

def isFile(path,extensionConstraints=None):
	if extensionConstraints:
		return os.path.isfile(path) and extension(path) in extensionConstraints
	return os.path.isfile(path) 

def path_to_dict(path):
	d = None
	if os.path.isdir(path):
		if os.path.basename(path) != "wikiconfig":
			d = {'name': os.path.basename(path)}
			d['type'] = "folder"
			directFolders = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path) if os.path.isdir(os.path.join(path,x))]
			d['folders'] = []
			for folder in directFolders:
				if folder:
					d['folders'].append(folder)
			d['files'] = [generateFileData(os.path.join(path,f)) for f in os.listdir(path) if isFile(os.path.join(path, f),extensionConstraints=[".md",".png",".jpg",".gif"])]
	return d


def validateDb(root_folder):
	dbpath = os.path.join(root_folder,"wikiconfig","wiki.db")
	if exists(dbpath):
		return True
	else:
		return False

def touch(path):
	with open(path, 'a'):
		os.utime(path, None)

def checkupWikiconfig(root_folder):

	wikiconfigpath = os.path.join(root_folder,"wikiconfig")
	if not exists(wikiconfigpath):
		try:
			os.makedirs(os.path.join(root_folder,"wikiconfig"))
		except Exception as E:
			return responseGenerator.createExceptionResponse("could not create wikiconfig folder : " + type(E).__name__ + " | " + str(E) )

	wikiDbExists = validateDb(root_folder)
	if not wikiDbExists:
		try:
			touch(os.path.join(root_folder,"wikiconfig","wiki.db"))
		except Exception as E:
			return responseGenerator.createExceptionResponse("could not create database file 'wiki.db' in wikiconfig : " + type(E).__name__ + " | " + str(E) )

	return responseGenerator.createSuccessResponse("wikiconfig is valid")
