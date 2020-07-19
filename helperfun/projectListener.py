import sublime
import logging
import sys
import time
import copy
from threading import Thread

from collections import deque

from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import sessionManager

class FileEventHandler(PatternMatchingEventHandler):

	def __init__(self,connection,patterns=None,ignore_directories=False):
		super(FileEventHandler,self).__init__(patterns=patterns,ignore_directories=ignore_directories)
		self.connection = connection

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
		pass
		#self.historyQueue.append({"type":"modified",
		#						"srcPath":event.src_path})


	def fetch(self):
		dCopy = copy.deepcopy(self.historyQueue)
		self.historyQueue.clear()

		return dCopy




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
				if q:
					for d in q:
						if d["type"] == "modified" or d["type"] == "created":
							d["content"] = FileListener.readFile(d["srcPath"])

					dict_wrapper = {"queue":[entry for entry in q]}

					self.connection.filesChanged(dict_wrapper)
			self.observer.stop()
		except Exception as e:
			print(e)
			self.observer.stop()
		self.observer.join()
		print(self.connection.isConnected())

		print("stopped observer")

	@staticmethod
	def readFile(path):
		try:
			return open(path, 'r', encoding='utf8').read()
		except Exception as e:
			sublime.error_message("could not read file:{0}, index of backend-server is broken now! initialize project again!!", path)
			return "BROKEN CONTENT"