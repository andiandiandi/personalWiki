import os
import time
import threading

from . import databaseManager
from . import pathManager


wikis = {}
_zombieCollector = None


############## session related #######################

def register(sid,socket):
	if not sid in wikis:
		wiki = Wiki(sid,socket)
		wikis[sid] = wiki
		return True
	else:
		return False

def remove(sid):
	if sid in wikis:
		del wikis[sid]

def wiki(sid):
	if sid in wikis:
		return wikis[sid]
	else:
		return None

class Wiki:
	def __init__(self,sid,socket):
		self.sid = sid
		self.socket = socket
		self.dbWrapper = None
		self.dbInit = False
		self.root_folder = None

	#returns false when something goes wrong
	def initializeProject(self, root_folder, json_project_structure):
		self.root_folder = root_folder
		self.dbWrapper = databaseManager.DbWrapper(self)
		self.dbConnectionEstablished = self.dbWrapper.create_connection()
		
		if self.dbConnectionEstablished:
			noerror = self.dbWrapper.checkIndex(json_project_structure)
			self.dbInit = True
			if noerror:
				return True

		return False

	def send(self,event,jsondata):
		self.socket.emit(event,jsondata,room=self.sid)

	def __del__(self):
		if self.dbWrapper:
			del self.dbWrapper