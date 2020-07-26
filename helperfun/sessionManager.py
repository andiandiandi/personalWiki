from . import configManager
from . import pathManager
from . import wikiSettingsManager
from . import localApi

import imp
from . import socketio

import time
import threading
import json
import os

_CONNECTIONSTRING = "http://127.0.0.1:9000"

imp.reload(configManager)
imp.reload(pathManager)
imp.reload(socketio)
imp.reload(wikiSettingsManager)
imp.reload(localApi)

connections = {}
_zombieCollector = None

def cleanup():
	print("cleaning up")
	for root_folder in connections:
		con = connections[root_folder]
		con.disconnect()
	
	connections.clear()

def add(root_folder):
	if not root_folder in connections:
		connections[root_folder] = Connection(root_folder)
		for c in connections:
			print("c",c)

	if not _zombieCollector:
	   run_zombieCollector()
	elif not _zombieCollector.isAlive():
	   run_zombieCollector()

	return connections[root_folder]


def remove(root_folder):
	if root_folder in connections:
		try:
			print("removing",root_folder)
			if connections[root_folder].isConnected():
				connections[root_folder].disconnect()
			del connections[root_folder]
		except Exception as e:
			print(type(e).__name__)
			print(e.args)


def createConnection(root_folder):
	return Connection(root_folder)

def hasProject(root_folder):
	return root_folder in connections

def connection(root_folder):
	if root_folder in connections:
		 return connections[root_folder]
	return None


class WikiState:
	disconnected = "disconnected"
	connected = "connected"
	projectInitialized = "project initialized"

class Connection:
	def __init__(self,root_folder):
		self.root_folder = root_folder
		self.socket = socketio.Client(reconnection = False)
		self.socket.on("connect", self.connectedEvent)
		self.socket.on("disconnect", self.disconnectedEvent)
		self.socket.on("error", self.errorEvent)
		self.socket.on("project_initialized", self.projectInitializeResponse)
		self.socket.on("search_query", self.searchQueryResponse)
		self.socket.on("files_changed", self.filesChangedResponse)
		self.socket.on("clear_db", self.clearWikiDatabaseResponse)
		self.socket.on("open_browser", self.openBrowserResponse)
		self.lock = threading.Lock()
		self.wikiState = WikiState.disconnected

	def sid(self):
		if self.socket and self.isConnected():
			return self.socket.sid

	def connect(self):
		if not self.socket.connected:
			try:
				self.socket.connect(_CONNECTIONSTRING)
			except:
				return False
		return True

	def disconnect(self):
		if self.socket.connected:
			print("disconnecting")
			self.socket.disconnect()
			if self.wikiState != WikiState.disconnected:
				self.updateWikiState(WikiState.disconnected)

	def updateWikiState(self,newState):
		self.wikiState = newState
		if self.wikiState == WikiState.disconnected:
			localApi.runWindowCommand(self.root_folder,"disconnect_wiki")

	def connectedEvent(self):
		print(self.socket.sid, "connected")
		self.updateWikiState(WikiState.connected)

	def disconnectedEvent(self):
		print("disconnected")
		if self.wikiState != WikiState.disconnected:
				self.updateWikiState(WikiState.disconnected)

	def projectInitializeResponse(self, jsondata):
		print("received projectInitializeResponse:", str(jsondata))
		self.updateWikiState(WikiState.projectInitialized)

	def filesChangedResponse(self,jsondata):
		print("filesres",jsondata)

	def clearWikiDatabaseResponse(self,jsondata):
		print(jsondata)

	def openBrowserResponse(self,pathStr):
		if type(pathStr) == str:
			localApi.runWindowCommand(self.root_folder,"render_wikipage",{"path":pathStr})

	def searchQueryResponse(self, jsondata):
		print("received searchQueryResponse:" + str(jsondata))
		#jsondata is no jsonstr
		d = json.loads(jsondata)
		print(type(d))
		l = []
		if d:
			for entry in d:
				if "span" in entry:
					for s in entry["span"]:
						fullpath = os.path.join(entry["file"]["path"],entry["file"]["name"] + entry["file"]["extension"])
						i = {"path":fullpath,
							"start":s["start"],
							"span":s["read"]
							}
						l.append(json.dumps(i))

		def on_done(index):
			if index >= 0:
				item = json.loads(l[index])
				print(item)
				localApi.sublime.active_window().run_command("open_view_at_line", {"viewname": item["path"],"line": item["start"]})
			  #  view = localApi.sublime.active_window().open_file(item["path"])
				#print(dir(view))
				#view.run_command("goto_line", {"line": item["start"]} )

		localApi.sublime.active_window().show_quick_panel(l, on_done)

	def isConnected(self):
		if self.socket:
			return self.socket.connected
		return False

	def errorEvent(self,data):
		localApi.error("Wiki server error: " + data)

	def clearWikiDatabase(self):
		d = {"root_folder":self.root_folder}
		self.send("clear_db",json.dumps(d))

	def projectInitialize(self):
		if self.isConnected():
		
		#	jsondata = pathManager.path_to_dict(self.root_folder)
		#	d = {
		#		"root_folder": self.root_folder,
		#		"project_structure": jsondata
		#	}
			self.send("initialize_project",self.root_folder)
		else:
			localApi.error("connect to wiki server first")

	def searchQuery(self,searchQuery):
		if self.isConnected():
			self.send("search_query", json.dumps(searchQuery))
		else:
			localApi.error("connect to wiki server first")

	def renderWikipage(self,path):
		if self.isConnected():
			self.send("render_wikipage",path)
		else:
			localApi.error("connect to wiki server first")

	def save(self,jsonfile):
		 if self.isConnected():
		 	self.send("save_file",json.dumps(jsonfile))
		 else:
		 	localApi.error("connect to wiki server first")

	def filesChanged(self,data,updateEvent="all"):
		jsondata = json.dumps(data)
		apiEvent = None
		if updateEvent == "all":
			apiEvent = "files_changed"
		elif updateEvent == "modified":
			apiEvent = "file_modified"
		elif updateEvent == "created":
			apiEvent = "file_created"
		elif updateEvent == "deleted":
			apiEvent = "file_deleted"
		elif updateEvent == "moved":
			apiEvent = "file_moved"

		if jsondata and apiEvent:
			self.send(apiEvent,jsondata)


	def send(self,event,message):
		with self.lock:
			if self.socket and self.isConnected():
				print("sending",event)
				print("sending",message)
				self.socket.emit(event,message)

############### threading section#################

def check_zombies_every_n_seconds():
	zombie_clear_interval = get_zombie_clear_interval() or 15

	while connections:
		active_windows = [(pathManager.root_folder(window)) for window in localApi.windows()]
		toDisconnect = [folder for folder in connections if folder not in active_windows]

		for folder in list(toDisconnect):
			remove(folder)

		time.sleep(zombie_clear_interval)


def run_zombieCollector():
	global _zombieCollector
	_zombieCollector = threading.Thread(target=check_zombies_every_n_seconds, daemon=True)
	_zombieCollector.start()

def stop_zombieCollector():
	global _zombieCollector
	if not _zombieCollector:
		return

	_zombieCollector.join()


def get_zombie_clear_interval():
	sublime_settings        = wikiSettingsManager.get("session")
	clear_sessions_interval    = sublime_settings.get('clear_sessions_interval', 15)

	#only unsigned integers for saving-interval
	if clear_sessions_interval <= 0:
		clear_sessions_interval = 15

	return clear_sessions_interval