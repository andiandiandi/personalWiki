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

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)

def plugin_loaded():	
	pass

def plugin_unloaded():
	sessionManager.cleanup()

class InitializeWikiProjectCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)

		if con:
			con.projectInitialize()
		else:
			sublime.error_message("connect to wiki server before initializing the project")

class RemoveWikiCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			sessionManager.remove(root_folder)

class DisconnectWikiCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)
			con.disconnect()

class SelContentCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)
		con.selContent()

class SelFilesCommand(sublime_plugin.TextCommand):
	
	def run(self,edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)
		con.selFiles()

class PrintProjectStructureCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		root_folder = pathManager.root_folder()
		structure = pathManager.path_to_dict(root_folder)
		print(structure)

class ClearWikiDatabaseCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)

		con.clearWikiDatabase()

class ConnectWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		window = self.view.window()

		root_folder = pathManager.root_folder()
		if not root_folder:
			return

		if sessionManager.hasProject(root_folder):
			sublime.error_message(root_folder + " already connected")
			return
		else:
			Connection = sessionManager.add(root_folder)
			connected = Connection.connect()

			if not connected:
				sublime.error_message("wiki server not running")