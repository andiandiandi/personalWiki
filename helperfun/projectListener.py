
import logging
import sys
import time
import copy
import os
from threading import Thread

from collections import deque

from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import sessionManager
from . import localApi
from threading import Lock

class FileEventHandler(PatternMatchingEventHandler):

	def __init__(self,connection,patterns=None,ignore_directories=False):
		super(FileEventHandler,self).__init__(patterns=patterns,ignore_directories=ignore_directories)
		self.connection = connection

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
		try:
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
		except Exception as e:
			print(str(e))


	def fetch(self):
		return self.accessQueue("fetch")




class FileListener:

	def __init__(self, path):
		self.path = path
		self.connection = sessionManager.connection(path)

		self.event_handler = FileEventHandler(self.connection,patterns=['*.md'],ignore_directories=True)
		self.observer = Observer()

	def start(self):
		thread = Thread(target = self.startObserver)
		thread.start()

	def startObserver(self):
		self.observer.schedule(self.event_handler, self.path, recursive=True)
		self.observer.start()
		try:
			while self.connection and self.connection.isConnected():
				time.sleep(4)
				q = self.event_handler.fetch()
				modifiedBookkeeping = {}
				if q:
					for d in q:
						if d["type"] == "modified" or d["type"] == "created":
							d["lastmodified"] = FileListener.readModifiedValue(d["srcPath"])
							print("here1")
							if d["srcPath"] in modifiedBookkeeping and modifiedBookkeeping[d["srcPath"]] == d["lastmodified"]:
								print("here2")
								d["valid"] = False
							else:
								print("here3")
								d["content"] = FileListener.readFile(d["srcPath"])
								modifiedBookkeeping[d["srcPath"]] = d["lastmodified"]
					dict_wrapper = {"queue":[entry for entry in q]}
					print(dict_wrapper)
					self.connection.filesChanged(dict_wrapper)
			self.observer.stop()
		except Exception as e:
			print("exception",str(e))
			self.observer.stop()
		self.observer.join()
		print("connected?",self.connection.isConnected())

		print("stopped observer")

	@staticmethod
	def readFile(path):
		try:
			return open(path, 'r', encoding='utf8').read()
		except Exception as e:
			localApi.error("could not read file:{0}, index of backend-server is broken now! initialize project again!!", path)
			return "BROKEN CONTENT"

	@staticmethod
	def readModifiedValue(path):
		try:
			return os.path.getmtime(path)
		except Exception as e:
			localApi.error("could not read modification-date of file:{0}, index of backend-server is broken now! initialize project again!!", path)
			return "BROKEN CONTENT"
