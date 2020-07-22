import os
import time
import threading
from enum import Enum  

from . import databaseManager
from . import pathManager
from . import projectListener
from . import responseGenerator


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
		self.fileListener = None

	def send(self,event,strdata):
		self.socket.emit(event, str(strdata), room = self.sid)

	#returns false when something goes wrong
	def initializeProject(self, root_folder, json_project_structure):
		if self.dbStatus == DbStatus.notConnected:
			self.connectToDatabase(root_folder)

		if self.dbStatus.value >= DbStatus.connectionEstablished.value:
			self.root_folder = root_folder
			noerror = self.dbWrapper.checkIndex(json_project_structure)
			if noerror:
				self.dbStatus = DbStatus.projectInitialized
				self.startFileListener()

				return responseGenerator.createSuccessResponse("project initialized")

		return responseGenerator.createExceptionResponse("could not initialize project")

	def connectToDatabase(self,root_folder):
		self.root_folder = root_folder
		self.dbWrapper = databaseManager.DbWrapper(self)
		dbConnectionEstablished = self.dbWrapper.create_connection()
		
		if dbConnectionEstablished:
			self.dbStatus = DbStatus.connectionEstablished
			return responseGenerator.createSuccessResponse("connected to Database")

		return responseGenerator.createExceptionResponse("could not connect to Database")

	def startFileListener(self):
		self.filelistener = projectListener.FileListener(self)
		self.filelistener.start()

	def send(self,event,jsondata):
		self.socket.emit(event,jsondata,room=self.sid)

	def __del__(self):
		if self.fileListener:
			self.fileListener.stop()
		if self.dbWrapper:
			del self.dbWrapper