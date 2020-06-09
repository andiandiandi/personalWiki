import sublime
import sublime_plugin
import os
import sys
import imp

from .helperfun import sessionManager
from .helperfun import pathManager
from .helperfun import localApi

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)

def plugin_loaded():	
	pass

def plugin_unloaded():
	pass

class DebugInitCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)
		con.disconnect()

class DebugDebugInitCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)
		print(con.window_ids)

class InitWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		window = self.view.window()

		root_folder = pathManager.root_folder()
		window_id = localApi.window_id()
		sessionManager.add(root_folder,window_id)
