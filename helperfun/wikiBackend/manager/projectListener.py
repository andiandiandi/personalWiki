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
from . import pathManager

INDEXINTERVAL = 2

class FileEventHandler(FileSystemEventHandler):

	def __init__(self):
		#super(FileEventHandler,self).__init__()
		self.historyQueue = deque()
		self.modifiedBookkeeping = {}
		self.lock = Lock()

	def clearBooking(self):
		self.modifiedBookkeeping.clear()

	def on_moved(self, event):
		if event.is_directory:
			return
		name, ext = os.path.splitext(event.src_path)
		if ext:
			if pathManager.isExtSupported(ext):
				print("MOVED",ext)
				self.accessQueue("moved",event)

	def on_created(self, event):
		if event.is_directory:
			return
		name, ext = os.path.splitext(event.src_path)
		if ext:
			if pathManager.isExtSupported(ext):
				print("created",event)
				self.accessQueue("created",event)

	def on_deleted(self, event):
		name, ext = os.path.splitext(event.src_path)
		if ext:
			if pathManager.isExtSupported(ext):
				print("deleted",event)
				self.accessQueue("deleted",event)
		else:
			self.accessQueue("deletedDirectoryGuess", event)

	def on_modified(self, event):
		if event.is_directory:
			return
		name, ext = os.path.splitext(event.src_path)
		if ext:
			if pathManager.isExtSupported(ext):
				print("MODIFIED",event)
				self.accessQueue("modified",event)

	def accessQueue(self,accessType,event=None):
		with self.lock:
			if accessType == "fetch":
				dCopy = copy.deepcopy(self.historyQueue)
				self.historyQueue.clear()
				return dCopy

			eventObj = None
			if accessType == "modified":
				eventObj = {"type":"modified",
								"srcPath":event.src_path,
							"valid": True}
			elif accessType == "created":
				eventObj = {"type":"created",
								"srcPath":event.src_path,
								"valid":True}
			elif accessType == "deleted":
				eventObj = {"type":"deleted",
								"srcPath":event.src_path,
								"valid":True}
			elif accessType == "moved":
				eventObj = {"type":"moved",
								"srcPath":event.src_path,
								 "destPath":event.dest_path,
								 "valid" : True}
			elif accessType == "deletedDirectoryGuess":
				eventObj = {"type":"deletedDirectoryGuess",
								"srcPath":event.src_path,
								 "valid" : True}

			if eventObj:
				if eventObj["type"] == "modified" or eventObj["type"] == "created" or eventObj["type"] == "moved":
					eventObj["lastmodified"] = FileSystemWatcher.readModifiedValue(eventObj["srcPath"] if eventObj["type"] != "moved" else eventObj["destPath"])
					if eventObj["srcPath"] in self.modifiedBookkeeping and self.modifiedBookkeeping[eventObj["srcPath"]] == eventObj["lastmodified"]:
						eventObj["valid"] = False
					else:
						self.modifiedBookkeeping[eventObj["srcPath"]] = eventObj["lastmodified"]
					if eventObj["type"] != "moved":
						if eventObj["valid"]:
							eventObj["content"] = pathManager.generateContent(eventObj["srcPath"])
					else:
						if eventObj["srcPath"] == eventObj["destPath"]:
							eventObj["valid"] = False

			self.historyQueue.append(eventObj)
			

	def fetch(self):
		return self.accessQueue("fetch")


class FileSystemWatcher:

	def __init__(self, callbackFileschanged, callbackError, root_folder):
		self.callbackFileschanged = callbackFileschanged
		self.callbackError = callbackError
		self.root_folder = root_folder
		self.shouldRun = False
		self.paused = False
		#patterns=['*'+ e for e in pathManager.supportedExtensions()]
		#ignore_directories=False
		self.event_handler = FileEventHandler()
		self.observer = Observer()

	def start(self):
		self.shouldRun = True
		thread = Thread(target = self.startObserver)
		thread.start()

	def stop(self):
		self.shouldRun = False
		print("shouldRun set=False at FileSystemWatcher")

	def pause(self):
		self.paused = True

	def resume(self):
		self.paused = False

	def isPaused(self):
		return self.paused

	def isRunning(self):
		return self.shouldRun

	def startObserver(self):
		print("started FileSystemWatcher")
		self.observer.schedule(self.event_handler, self.root_folder, recursive=True)
		self.observer.start()
		try:
			while self.shouldRun:
				global INDEXINTERVAL
				time.sleep(INDEXINTERVAL)
				if not self.shouldRun:
					break
				if self.isPaused():
					continue
				q = self.event_handler.fetch()
				self.event_handler.clearBooking()
				"""
				modifiedBookkeeping = {}
				if q:
					for d in q:
						if d["type"] == "modified" or d["type"] == "created" or d["type"] == "moved":
							d["lastmodified"] = FileSystemWatcher.readModifiedValue(d["srcPath"] if d["type"] != "moved" else d["destPath"])
							if d["srcPath"] in modifiedBookkeeping and modifiedBookkeeping[d["srcPath"]] == d["lastmodified"]:
								d["valid"] = False
							else:
								modifiedBookkeeping[d["srcPath"]] = d["lastmodified"]
							if d["type"] != "moved":
								d["content"] = pathManager.generateContent(d["srcPath"])
							else:
								if d["srcPath"] == d["destPath"]:
									d["valid"] = False

					modifiedBookkeeping.clear()
				"""
				if q:
					dict_wrapper = {"queue":[entry for entry in q]}
					result = self.callbackFileschanged(dict_wrapper)
		except Exception as e:
			self.observer.stop()
			self.callbackError("FilesystemWatcher stopped: " + str(e))
		self.observer.stop()
		self.observer.join()
		print("stopped FileSystemWatcher")
		

	@staticmethod
	def readModifiedValue(path):
		try:
			return os.path.getmtime(path)
		except Exception as e:
			print("EXCEPTION in readmodi projectlistener:",str(e))
			return "Excp in readModifiedValue:" + str(e)