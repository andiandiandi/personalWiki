import sublime
import sublime_plugin
import os
import sys
import imp

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
	pass

class DebugInitCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)
		con.send("debug","test")

class DebugDebugInitCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		saver.debug(root_folder)

class InitWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		window = self.view.window()

		root_folder = pathManager.root_folder()
		window_id = localApi.window_id()
		Connection = sessionManager.createConnection(root_folder,window_id)
		Connection.connect()
		if Connection.socket.connected:
			sessionManager.add(Connection.path,window_id)
		else:
			Connection.disconnect()
			Connection = None
			
		saver.save(root_folder)