import os
import time
import threading
from enum import Enum

from . import databaseManager
from . import pathManager
from . import projectListener
from . import responseGenerator


wikis = {}
subscribers = {}
_zombieCollector = None

def addSubscriber(socketSid,targetSid,eventname,socket,namespace,path):
	if not socketSid in subscribers:
		sub = Subscriber(socketSid,targetSid,eventname,socket,namespace,path=path)
		subscribers[socketSid] = sub
		print("ADDED SUB",sub.socketSid)
		print("ADDED SUB",eventname)
		print("ADDED SUB",namespace)
		return True
	else:
		sub = subscribers[socketSid]
		sub.addIdentity(eventname,path)
		return True
	return False

def removeSubscriber(socketSid):
	if socketSid in subscribers:
		del subscribers[socketSid]
		print("deleted sub",socketSid)

def notifySubscribers(eventname,targetSid,jsondata=None,path=None):
	notified = False
	if subscribers:
		for sub in subscribers.values():
			print("SID OF SUB",sub.socketSid)
			print("EVENTNAME FOR SUB",eventname)
			print("PATH OF SUB",path)
			if sub.hasIdentity(eventname,path) and sub.hasTarget(targetSid):
				sub.send(eventname,jsondata)
				notified = True
	return notified

def register(sid,socket):
	if not sid in wikis:
		wiki = Wiki(sid,socket)
		wikis[sid] = wiki
		return True
	else:
		return False

def remove(sid):
	if sid in wikis:
		wikis[sid].cleanup()
		wikis[sid] = None
		del wikis[sid]

def wiki(sid):
	if sid in wikis:
		return wikis[sid]
	else:
		return None

def hasConnections():
	return wikis is not None

def sids():
	return wikis.keys()

class DbStatus(Enum):
	notConnected = 0
	connectionEstablished = 1
	projectInitialized = 2

class Subscriber:
	def __init__(self,socketSid,targetSid,eventname,socket,namespace,path=None):
		self.socketSid = socketSid
		self.targetSid = targetSid
		self.socket = socket
		self.identifier = {}
		self.identifier[eventname] = path
		self.namespace = namespace
	def hasTarget(self,targetSid):
		return self.targetSid == targetSid

	def hasPath(self,path):
		return self.path == path

	def hasIdentity(self,eventname,path):
		if eventname in self.identifier:
			return self.identifier[eventname] == path

	def addIdentity(self,eventname,path):
		if eventname not in self.identifier:
			self.identifier[eventname] = path

	def send(self,event,jsondata):
		self.socket.emit(event,jsondata,room=self.socketSid,namespace=self.namespace)

class Wiki:
	def __init__(self,sid,socket):
		self.sid = sid
		self.socket = socket
		self.Indexer = None
		self.dbStatus = DbStatus.notConnected
		self.root_folder = None
		self.FileSystemWatcher = None

	def send(self,event,strdata):
		self.socket.emit(event, strdata, room = self.sid)

	def cleanup(self):
		if self.FileSystemWatcher:
			self.FileSystemWatcher.stop()
		if self.Indexer:
			self.Indexer.closeConnection()
			del self.Indexer

	def initializeProject(self, root_folder):
		if self.dbStatus == DbStatus.notConnected:
			response = pathManager.checkupWikiconfig(root_folder)
			if response["status"] == "exception":
				return response
			self.connectToDatabase(root_folder)

		if self.dbStatus.value >= DbStatus.connectionEstablished.value:
			self.root_folder = root_folder
			if self.FileSystemWatcher and self.FileSystemWatcher.isRunning():
				self.FileSystemWatcher.pause()
			response = self.Indexer.checkIndex()
			if self.FileSystemWatcher and self.FileSystemWatcher.isPaused():
				self.FileSystemWatcher.resume()
			if response["status"] != "exception":
				self.dbStatus = DbStatus.projectInitialized
				self.startFileSystemWatcher()

				return responseGenerator.createSuccessResponse("project initialized")
			else:
				return response

		return responseGenerator.createExceptionResponse("could not initialize project")

	def connectToDatabase(self,root_folder):
		self.root_folder = root_folder
		self.Indexer = databaseManager.Indexer(self)
		dbConnectionEstablished = self.Indexer.create_connection()
		
		if dbConnectionEstablished:
			self.dbStatus = DbStatus.connectionEstablished
			return responseGenerator.createSuccessResponse("connected to Database")

		return responseGenerator.createExceptionResponse("could not connect to Database")

	def startFileSystemWatcher(self):
		if self.FileSystemWatcher and self.FileSystemWatcher.isRunning():
			return
		self.FileSystemWatcher = projectListener.FileSystemWatcher(self)
		self.FileSystemWatcher.start()

	def send(self,event,jsondata):
		self.socket.emit(event,jsondata,room=self.sid)