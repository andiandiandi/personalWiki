import os
import time
import threading
from enum import Enum  

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

def hasConnections():
	return wikis is not None

class DbStatus(Enum):
	notConnected = 0
	connectionEstablished = 1
	projectInitialized = 2


class Wiki:
	def __init__(self,sid,socket):
		self.sid = sid
		self.socket = socket
		self.dbWrapper = None
		self.dbStatus = DbStatus.notConnected
		self.root_folder = None

	#returns false when something goes wrong
	def initializeProject(self, root_folder, json_project_structure):
		if self.dbStatus == DbStatus.notConnected:
			self.connectToDatabase(root_folder)

		if self.dbStatus == DbStatus.connectionEstablished:
			self.root_folder = root_folder
			noerror = self.dbWrapper.checkIndex(json_project_structure)
			if noerror:
				return True

		return False

	def connectToDatabase(self,root_folder):
		self.root_folder = root_folder
		self.dbWrapper = databaseManager.DbWrapper(self)
		dbConnectionEstablished = self.dbWrapper.create_connection()
		
		if dbConnectionEstablished:
			self.dbStatus = DbStatus.connectionEstablished
			return True

		return False

	def send(self,event,jsondata):
		self.socket.emit(event,jsondata,room=self.sid)

	def __del__(self):
		if self.dbWrapper:
			del self.dbWrapper