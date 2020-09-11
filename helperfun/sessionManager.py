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

imp.reload(pathManager)
imp.reload(socketio)
imp.reload(wikiSettingsManager)
imp.reload(localApi)

connections = {}
_zombieCollector = None

def cleanup():
	for root_folder in connections:
		con = connections[root_folder]
		con.disconnect()
	
	connections.clear()

def add(root_folder):
	if not root_folder in connections:
		connections[root_folder] = Connection(root_folder)

	if not _zombieCollector:
	   run_zombieCollector()
	elif not _zombieCollector.isAlive():
	   run_zombieCollector()

	return connections[root_folder]


def remove(root_folder):
	if root_folder in connections:
		try:
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
		self.socket.on("files_changed", self.filesChangedResponse)
		self.socket.on("clear_db", self.clearWikiDatabaseResponse)
		self.socket.on("open_browser", self.openBrowserResponse)
		self.socket.on("sel_content",self.selContentResponse)
		self.socket.on("sel_files",self.selFilesResponse)
		self.socket.on("word_count", self.wordCountResponse)
		self.socket.on("create_wikilink", self.createWikilinkResponse)
		self.socket.on("saved_search_query",self.savedSearchQueryResponse)
		self.socket.on("search_query", self.searchQueryResponse)
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
			self.socket.disconnect()
			if self.wikiState != WikiState.disconnected:
				self.updateWikiState(WikiState.disconnected)

	def updateWikiState(self,newState):
		self.wikiState = newState
		print(newState)
		if self.wikiState == WikiState.disconnected:
			localApi.runWindowCommand(self.root_folder,"remove_wiki")

	def connectedEvent(self):
		print(self.socket.sid, "connected")
		self.updateWikiState(WikiState.connected)

	def disconnectedEvent(self):
		if self.wikiState != WikiState.disconnected:
			self.updateWikiState(WikiState.disconnected)

	def projectInitializeResponse(self, jsondata):
		print("received projectInitializeResponse:", str(jsondata))
		self.updateWikiState(WikiState.projectInitialized)

	def createWikilinkResponse(self,data):
		try:
			d = json.loads(data)
			if d["type"] == "directlink":
				files = d["files"]
				localApi.runWindowCommand(self.root_folder,"create_wikilink",args={"files":files})
			elif d["type"] == "create":
				templates = d["templates"]
				folders = d["folders"]
				filename = d["filename"]
				localApi.runWindowCommand(self.root_folder,"show_wikilink_options",args={"templates":templates,"folders":folders,"filename":filename})
			elif d["type"] == "directimagelink":
				files = d["files"]
				localApi.runWindowCommand(self.root_folder,"create_imagelink",args={"files":files})
			elif d["type"] == "createimagelink":
				localApi.runWindowCommand(self.root_folder,"create_imagelink")

		except:
			return

	def savedSearchQueryResponse(self,data):
		localApi.runWindowCommand(self.root_folder,"saved_search_query",args={"d":data})

	def selContentResponse(self,data):
		print(data)

	def selFilesResponse(self,data):
		print(data)

	def wordCountResponse(self,data):
		localApi.runWindowCommand(self.root_folder,"show_word_count",args={"d":data})

	def filesChangedResponse(self,jsondata):
		print(jsondata)

	def clearWikiDatabaseResponse(self,jsondata):
		print(jsondata)

	def openBrowserResponse(self,pathStr):
		if type(pathStr) == str:
			localApi.runWindowCommand(self.root_folder,"render_wikipage",{"path":pathStr})

	def searchQueryResponse(self, jsondata):
		localApi.runWindowCommand(self.root_folder,"show_search_result",args={"queryResult":jsondata})

	def isConnected(self):
		if self.socket:
			return self.socket.connected
		return False

	def errorEvent(self,data):
		localApi.error("Wiki server error: " + data)


	def createWikilink(self,data):
		print("EEE",data)
		if self.isConnected():
			#self.send("create_wikilink", json.dumps({"filename":filename,"srcPath":srcPath}))
			self.send("create_wikilink", json.dumps(data))
		else:
			localApi.error("connect to wiki server first")


	def selContent(self):
		self.send("sel_content","")

	def selFiles(self):
		self.send("sel_files","")

	def clearWikiDatabase(self):
		d = {"root_folder":self.root_folder}
		self.send("clear_db",json.dumps(d))

	def deleteSavedQuery(self,query):
		print("DELETESAVEDQUERY:" + query)
		return
		if self.isConnected():
			self.send("delete_saved_query",self.root_folder)
		else:
			localApi.error("connect to wiki server first")

	def savedSearchQuery(self):
		if self.isConnected():
			self.send("saved_search_query",self.root_folder)
		else:
			localApi.error("connect to wiki server first")

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
		print(searchQuery)
		if self.isConnected():
			self.send("search_query", searchQuery)
		else:
			localApi.error("connect to wiki server first")

	def renderWikipage(self,path):
		if self.isConnected():
			self.send("render_wikipage",path)
		else:
			localApi.error("connect to wiki server first")

	def wordCount(self,path=None):
		if self.isConnected():
			if path:
				self.send("word_count",path)
			else:
				self.send("word_count","")
		else:
			localApi.error("connect to wiki server first")


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