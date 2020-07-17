import sublime
import sublime_plugin
import os
import sys
import imp
import json

import platform
import subprocess

from .helperfun import sessionManager
from .helperfun import pathManager
from .helperfun import localApi
from .helperfun import saver

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)
imp.reload(saver)

def plugin_loaded():	
	pass

def plugin_unloaded():
	sessionManager.cleanup()

class DebugInitCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)

		if con:
			con.projectInitialize()
		else:
			sublime.error_message("connect to wiki server before initializing the project")

class DisconnectWikiCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		sessionManager.remove(root_folder)



class SearchQueryHeadersCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)

		jsonsearch = {"files":{"negate":False,"values":["nicefile.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header 222"}]}
		jsonsearch2 = {"files":{"negate":False,"values":["subtestfile.md"]},"element":{"negate":False, "value":"headers"},"values":[]}

		con.searchQuery(jsonsearch)



class InitWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		window = self.view.window()

		root_folder = pathManager.root_folder()
		if not root_folder:
			return
		print(root_folder)

		#window_id = localApi.window_id()
		if sessionManager.hasProject(root_folder):
			print("already connected")
			return
		else:
			configExists = validateWikiconfig(root_folder)
			if not configExists:
				os.makedirs(os.path.join(root_folder,"wikiconfig"))

			wikiDbExists = validateDb(root_folder)
			if not wikiDbExists:
				touch(os.path.join(root_folder,"wikiconfig","wiki.db"))



			Connection = sessionManager.add(root_folder)
			connected = Connection.connect()

			if not connected:
				sublime.error_message("wiki server not running")


def startServer():
	DETACHED_PROCESS = 0x00000008

	print(os.path.join(pathManager.path_to_helperfun(),"wikiBackend","socketServer.py"))
	pid = subprocess.Popen([sys.executable, os.path.join(pathManager.path_to_helperfun(),"wikiBackend","socketServer.py")],
                       creationflags=DETACHED_PROCESS).pid
	print(pid)

def validateWikiconfig(root_folder):
	wikiconfigpath = os.path.join(root_folder,"wikiconfig")
	if pathManager.exists(wikiconfigpath):
		return True
	else:
		return False

def validateDb(root_folder):
	dbpath = os.path.join(root_folder,"wikiconfig","wiki.db")
	if pathManager.exists(dbpath):
		return True
	else:
		return False

def createWikiconfig(root_folder):
	pass

def createWikidb(root_folder):
	pass

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)