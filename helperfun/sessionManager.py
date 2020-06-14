from . import configManager
from . import pathManager
from . import wikiSettingsManager
from . import localApi

import imp
from . import socketio

import time
import threading

_CONNECTIONSTRING = "http://127.0.0.1:9000"

imp.reload(configManager)
imp.reload(pathManager)
imp.reload(socketio)
imp.reload(wikiSettingsManager)
imp.reload(localApi)

connections = {}
_zombieCollector = None

def add(root_folder,window_id):
	if not root_folder in connections:
		connections[root_folder] = Connection(root_folder,window_id)
	else:
		Con = connections[root_folder]
		if window_id not in Con.window_ids:
			Con.add_window_id(window_id)

	if not _zombieCollector:
		run_zombieCollector()
	elif not _zombieCollector.isAlive():
		run_zombieCollector()

	return connections[root_folder]


def remove(root_folder):
	if root_folder in connections:
		try:
			connections[root_folder].disconnect()
			connections[root_folder] = None
			del connections[root_folder]
		except:
			connections[root_folder] = None
			del connections[root_folder]

def createConnection(root_folder,window_id):
	return Connection(root_folder,window_id)

def connection(path):
	return connections[path]

class Connection:
	def __init__(self,path,window_id):
		self.path = path
		self.window_ids = [window_id]
		self.socket = socketio.Client(reconnection = True)
		self.socket.on("connect",self.connected)
		self.socket.on("disconnect",self.disconnected)
		self.socket.on("debug",self.debug)

	def add_window_id(self,window_id):
		if window_id not in self.window_ids:
			self.window_ids.append(window_id)

	def connect(self):
		if not self.socket.connected:
			self.socket.connect(_CONNECTIONSTRING)

	def disconnect(self):
		if self.socket.connected:
			print("disconnecting")
			self.socket.disconnect()

	def connected(self):
		print(self.socket.sid, "connected")

	def disconnected(self):
		print(self.socket.sid, "disconnected")

	def debug(self,data):
		print("debug event:",data)

	def send(self,event,message):
		self.socket.emit(event,message)

############### threading section#################

def check_zombies_every_n_seconds():
	zombie_clear_interval = get_zombie_clear_interval()
	while connections:
		active_windows = [(window.id(),pathManager.root_folder(window)) for window in localApi.windows()]

		for con in list(connections.values()):
			#iterate over copy
			for id in list(con.window_ids):
				if (id,con.path) not in active_windows:
					con.window_ids.remove(id)
					print("removing from con:",id)

		to_remove = [k for k in connections.keys() if not connections[k].window_ids]
		for k in to_remove: 
			remove(k)
			print("removing",k)

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
	sublime_settings 	    = wikiSettingsManager.get("session")
	clear_sessions_interval    = sublime_settings.get('clear_sessions_interval', 15)

	#only unsigned integers for saving-interval
	if clear_sessions_interval <= 0:
		clear_sessions_interval = 15

	return clear_sessions_interval