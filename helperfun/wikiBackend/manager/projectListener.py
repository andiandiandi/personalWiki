import logging
import sys
import time
import copy
import os
from threading import Thread

from collections import deque

from .libs.watchdog.events import PatternMatchingEventHandler
from .libs.watchdog.events import FileSystemEventHandler
from .libs.watchdog.observers import Observer

from . import sessionManager

class FileEventHandler(PatternMatchingEventHandler):

	def __init__(self,patterns=None,ignore_directories=False):
		super(FileEventHandler,self).__init__(patterns=patterns,ignore_directories=ignore_directories)
		self.historyQueue = deque()

	def on_moved(self, event):
		self.historyQueue.append({"type":"moved",
								"srcPath":event.src_path,
							 "destPath":event.dest_path
					})

	def on_created(self, event):
		self.historyQueue.append({"type":"created",
								"srcPath":event.src_path})

	def on_deleted(self, event):
		self.historyQueue.append({"type":"deleted",
								"srcPath":event.src_path})

	def on_modified(self, event):
		self.historyQueue.append({"type":"modified",
								"srcPath":event.src_path})


	def fetch(self):
		dCopy = copy.deepcopy(self.historyQueue)
		self.historyQueue.clear()

		return dCopy




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

	def startObserver(self):
		self.observer.schedule(self.event_handler, self.wiki.root_folder, recursive=True)
		self.observer.start()
		try:
			while self.shouldRun:
				time.sleep(4)
				q = self.event_handler.fetch()

				if self.wiki.dbStatus == sessionManager.DbStatus.projectInitialized:
					if q:
						for d in q:
							if d["type"] == "modified" or d["type"] == "created":
								d["content"] = FileListener.readFile(d["srcPath"])
								d["lastmodified"] = FileListener.readModifiedValue(d["srcPath"])
	# 
						dict_wrapper = {"queue":[entry for entry in q]}

						result = self.wiki.dbWrapper.filesChanged(dict_wrapper)
						self.wiki.send("files_changed",str(result))

			self.observer.stop()
		except Exception as e:
			self.wiki.send("error",str(e))
			self.observer.stop()
			self.wiki.dbStatus = sessionManager.DbStatus.connectionEstablished
		self.observer.join()

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