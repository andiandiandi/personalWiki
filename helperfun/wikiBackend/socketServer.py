from flask import Flask, render_template, request
from flask_socketio import SocketIO

from manager import sessionManager

import json
import time
import threading
import sys

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

@socketio.on('clear_db')
def on_clearDB(jsonStr):
	wiki = get(request.sid)
	if wiki.dbStatus == sessionManager.DbStatus.notConnected:
		realJson = json.loads(jsonStr)
		root_folder = realJson["root_folder"]
		connected = wiki.connectToDatabase(root_folder)
		if not connected:
			error("could not connect to database",request.sid)
	result = wiki.dbWrapper.clearDatabase()
	print("RESULT",result)
	socketio.emit("clear_db", json.dumps(result), room = request.sid)

@socketio.on('search_query')
def on_searchQuery(jsonStr):
	wiki = get(request.sid)
	if wiki.dbInit:
		result = wiki.dbWrapper.runSearchQuery(json.loads(jsonStr))
		socketio.emit("search_query", json.dumps(result), room = request.sid)
	else:
		error("you have to initialize the database first", request.sid)

@socketio.on('save_file')
def on_saveFile(jsonStr):
	wiki = get(request.sid)
	if wiki.dbInit:
		result = wiki.dbWrapper.saveFile(json.loads(jsonStr))
		socketio.emit("save_file", str(result), room = request.sid)
	else:
		error("you have to initialize the database first", request.sid)

@socketio.on('files_changed')
def on_filesChanged(jsonStr):
	wiki = get(request.sid)
	if wiki.dbInit:
		result = wiki.dbWrapper.filesChanged(json.loads(jsonStr))
		socketio.emit("files_changed", str(result), room = request.sid)
	else:
		error("you have to initialize the database first", request.sid)

@socketio.on('file_modified')
def on_fileModified(jsonStr):
	print(jsonStr)

@socketio.on('file_created')
def on_fileCreated(jsonStr):
	print(jsonStr)

@socketio.on('file_delete')
def on_fileDeleted(jsonStr):
	print(jsonStr)

@socketio.on('file_moved')
def on_fileMoved(jsonStr):
	print(jsonStr)

socketio.run(app, host="127.0.0.1", port=9000)
	

