from manager import sessionManager
import json

connections = {}

def error(message,sid):
	if sid in connections:
		connections[sid].emit("error",message,sid)

def get(sid):
	wiki = sessionManager.wiki(sid)
	if wiki:
		return wiki
	else:
		error("you have to connect to server first", sid)
		return None

def on_connect(sid,Socket):
	success = sessionManager.register(sid,Socket)
	if not success:
		error("could not register socket",sid)
		return
	connections[sid] = Socket

def on_disconnect(sid):
	sessionManager.remove(sid)

def on_initializeProject(sid,jsonStr):
	realJson = json.loads(jsonStr)
	root_folder = realJson["root_folder"]
	json_project_structure = realJson["project_structure"]
	wiki = get(sid)
	initialized = wiki.initializeProject(root_folder,json_project_structure)
	if not initialized:
		error("something went wrong while initializing project", sid)
	else:
		connections[sid].emit("project_initialized","successfully initialized project", room = sid)

def on_initializeProject(sid,root_folder,Socket):
	wiki = sessionManager.wiki(sid)
	if not wiki:
		success = sessionManager.register(sid,Socket)
		if not success:
			error("could not register wiki,socketid:",sid)
		connections[sid] = Socket
	wiki = get(sid)
	response = wiki.initializeProject(root_folder)
	if response["status"] == "exception":
		error("exception while init project: " + response["response"], sid)
	elif response["status"] == "success":
		connections[sid].emit("project_initialized","successfully initialized project", room = sid)
	else:
		connections[sid].emit("project_initialized","uninteded behaviour while init project", room = sid)


def on_selFiles(sid,jsonStr):
	wiki = get(sid)
	content = wiki.dbWrapper.selFilesDEBUG()
	connections[sid].emit("sel_files",str(content),room=sid)

def on_selImages(sid,jsonStr):
	wiki = get(sid)
	content = wiki.dbWrapper.selImagesDEBUG()
	connections[sid].emit("sel_images",str(content),room=sid)

def on_fileRenamed(sid,srcPath,destPath):
	wiki = get(sid)
	content = wiki.dbWrapper.fileRenamedTrigger(srcPath,destPath,"md")
	connections[sid].emit("file_renamed",str(content),room=sid)


def on_moveFile(sid,srcPath,destPath):
	wiki = get(sid)
	response = wiki.dbWrapper.moveFile(srcPath,destPath,1234)
	connections[sid].emit("files_changed",str(response),room=sid)

def on_clearDB(sid,jsonStr):
	wiki = get(sid)
	if wiki.dbStatus == sessionManager.DbStatus.notConnected:
		realJson = json.loads(jsonStr)
		root_folder = realJson["root_folder"]
		connected = wiki.connectToDatabase(root_folder)
		if not connected:
			error("could not connect to database",sid)
			return
			
	result = wiki.dbWrapper.clearDatabase()
	connections[sid].emit("clear_db", json.dumps(result), room = sid)

def on_searchQuery(sid,jsonStr):
	wiki = get(sid)
	if wiki.dbStatus == sessionManager.DbStatus.projectInitialized:
		result = wiki.dbWrapper.runSearchQuery(json.loads(jsonStr))
		connections[sid].emit("search_query", json.dumps(result), room = sid)
	else:
		error("you have to initialize the database first", sid)


def on_filesChanged(sid,jsonStr):
	wiki = get(sid)
	if wiki.dbStatus == sessionManager.DbStatus.projectInitialized:
		result = wiki.dbWrapper.filesChanged(json.loads(jsonStr))
		connections[sid].emit("files_changed", str(result), room = sid)
	else:
		error("you have to initialize the database first", sid)

def on_fileModified(jsonStr):
	print(jsonStr)

def on_fileCreated(jsonStr):
	print(jsonStr)

def on_fileDeleted(jsonStr):
	print(jsonStr)

def on_fileMoved(jsonStr):
	print(jsonStr)

