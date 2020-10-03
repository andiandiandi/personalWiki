import os
from .wikiManager import Wiki


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
