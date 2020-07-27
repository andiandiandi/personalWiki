import logging
import sys
import time
import copy
import os
import json
from threading import Thread
from threading import Lock

from collections import deque

from .libs.watchdog.events import PatternMatchingEventHandler
from .libs.watchdog.events import FileSystemEventHandler
from .libs.watchdog.observers import Observer

from . import sessionManager


class FileEventHandler(PatternMatchingEventHandler):

	def __init__(self,patterns=None,ignore_directories=False):
		super(FileEventHandler,self).__init__(patterns=patterns,ignore_directories=ignore_directories)
		self.historyQueue = deque()
		self.lock = Lock()

	def on_moved(self, event):
		self.accessQueue("moved",event)

	def on_created(self, event):
		self.accessQueue("created",event)

	def on_deleted(self, event):
		self.accessQueue("deleted",event)

	def on_modified(self, event):
		self.accessQueue("modified",event)

	def accessQueue(self,accessType,event=None):
		with self.lock:
			if accessType == "fetch":
				dCopy = copy.deepcopy(self.historyQueue)
				self.historyQueue.clear()
				return dCopy
			elif accessType == "modified":
				self.historyQueue.append({"type":"modified",
								"srcPath":event.src_path,
								"valid":True})
			elif accessType == "created":
				self.historyQueue.append({"type":"created",
								"srcPath":event.src_path,
								"valid":True})
			elif accessType == "deleted":
				self.historyQueue.append({"type":"deleted",
								"srcPath":event.src_path,
								"valid":True})
			elif accessType == "moved":
				self.historyQueue.append({"type":"moved",
								"srcPath":event.src_path,
							 "destPath":event.dest_path,
							 "valid" : True
					})

	def fetch(self):
		return self.accessQueue("fetch")


class FileListener:

	def __init__(self, wiki):
		self.wiki = wiki
		self.shouldRun = False
		self.event_handler = FileEventHandler(patterns=['*.md'],ignore_directories=True)
		self.observer = Observer()

	def start(self):
		self.shouldRun = True
		thread = Thread(target = self.startObserver)
		thread.start()

	def stop(self):
		self.shouldRun = False
		print("stopped filelistener")

	def startObserver(self):
		print("started filelistener")
		self.observer.schedule(self.event_handler, self.wiki.root_folder, recursive=True)
		self.observer.start()
		try:
			while self.shouldRun:
				time.sleep(4)
				q = self.event_handler.fetch()
				modifiedBookkeeping = {}
				if self.wiki.dbStatus == sessionManager.DbStatus.projectInitialized:
					if q:
						for d in q:
							if d["type"] == "modified" or d["type"] == "created" or d["type"] == "moved":
								d["lastmodified"] = FileListener.readModifiedValue(d["srcPath"] if d["type"] != "moved" else d["destPath"])
								if d["srcPath"] in modifiedBookkeeping and modifiedBookkeeping[d["srcPath"]] == d["lastmodified"]:
									d["valid"] = False
								else:
									modifiedBookkeeping[d["srcPath"]] = d["lastmodified"]
								if d["type"] != "moved":
									d["content"] = FileListener.readFile(d["srcPath"])
						modifiedBookkeeping.clear()
						dict_wrapper = {"queue":[entry for entry in q]}
						result = self.wiki.dbWrapper.filesChanged(dict_wrapper)
						self.wiki.send("files_changed",str(result) + " | " + json.dumps(dict_wrapper))
			self.observer.stop()
		except Exception as e:
			self.wiki.send("error","exception in startObeserver:" + str(e))
			self.observer.stop()
			self.wiki.dbStatus = sessionManager.DbStatus.connectionEstablished
		self.observer.join()

	@staticmethod
	def readFile(path):
		try:
			return open(path, 'r', encoding='utf8').read()
		except Exception as e:
			print("EXCEPTION in reafile projectlistener:", str(e))
			return "Excp in readFile:" + str(e)

	@staticmethod
	def readModifiedValue(path):
		try:
			return os.path.getmtime(path)
		except Exception as e:
			print("EXCEPTION in readmodi projectlistener:",str(e))
			return "Excp in readModifiedValue:" + str(e)