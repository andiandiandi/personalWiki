import sublime
import sublime_plugin
import os
import sys
import imp
import json

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

		con.projectInitialize()

class DebugDebugInitCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		saver.debug(root_folder)


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
		if sessionManager.isConnected(root_folder):
			print("already connected")
			return
		else:
			configExists = validateWikiconfig(root_folder)
			if not configExists:
				os.makedirs(os.path.dirname(os.path.join(root_folder,"wikiconfig")), exist_ok=True)

			wikiDbExists = validateDb(root_folder)
			if not wikiDbExists:
				touch(os.path.join(root_folder,"wikiconfig","wiki.db"))

			Connection = sessionManager.add(root_folder)
			Connection.connect()


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