from manager import sessionManager

globalsocket = None

def error(message,sid):
	globalsocket.emit("error",message,sid)

def get(sid):
	wiki = sessionManager.wiki(sid)
	if wiki:
		return wiki
	else:
		error("you have to connect to server first", sid)
		return None

def on_connect(sid,Socket):
	global globalsocket
	globalsocket = Socket
	success = sessionManager.register(sid,Socket)
	if not success:
		error("could not register socket",sid)

def on_disconnect(sid):
	sessionManager.remove(sid)

def on_initdb(sid,json_project_structure):
	wiki = get(sid)
	initialized = wiki.initializeDb(json_project_structure)
	if not initialized:
		error("you have to connect to server first", sid)

def on_search(sid,query):
	wiki = get(sid)
	if wiki.dbInit:
		result = wiki.dbWrapper.runSearchQuery(query)
		wiki.send("search",result)
	else:
		error("you have to initialie the database first", sid)


