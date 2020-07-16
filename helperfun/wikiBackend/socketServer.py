from flask import Flask, render_template, request
from flask_socketio import SocketIO

from manager import sessionManager

import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def error(message,sid):
	socketio.emit('error', message, room=sid)

def get(sid):
	wiki = sessionManager.wiki(sid)
	if wiki:
		return wiki
	else:
		error("you have to connect to server first", sid)
		return None

@socketio.on("connect")
def connect():
	success = sessionManager.register(request.sid,socketio)
	if not success:
		error("could not register socket",sid)

@socketio.on('disconnect')
def test_disconnect():
	sessionManager.remove(request.sid)

@socketio.on('debug')
def handle_message(message):
	socketio.emit('debug', str(wikiManager.sessions_count()), room = request.sid)

@socketio.on('initialize_project')
def on_initializeProject(jsonStr):
	realJson = json.loads(jsonStr)
	root_folder = realJson["root_folder"]
	json_project_structure = realJson["project_structure"]
	wiki = get(request.sid)
	initialized = wiki.initializeProject(root_folder,json_project_structure)
	if not initialized:
		error("something went wrong while initializing project", request.sid)
	else:
		socketio.emit("project_initialized","successfully initialized project", room = request.sid)

@socketio.on('search_query')
def on_searchQuery(jsonStr):
	wiki = get(request.sid)
	if wiki.dbInit:
		result = wiki.dbWrapper.runSearchQuery(json.loads(jsonStr))
		print("here")
		socketio.emit("search_query", str(result), room = request.sid)
	else:
		error("you have to initialize the database first", request.sid)

@socketio.on('save_file')
def on_searchQuery(jsonStr):
	wiki = get(request.sid)
	if wiki.dbInit:
		result = wiki.dbWrapper.saveFile(json.loads(jsonStr))
		socketio.emit("save_file", str(result), room = request.sid)
	else:
		error("you have to initialize the database first", request.sid)

if __name__ == '__main__':
	socketio.run(app, host="127.0.0.1", port=9000)