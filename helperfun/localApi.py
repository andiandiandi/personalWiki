import sublime
import imp

from . import pathManager

imp.reload(pathManager)

def windows():
	return sublime.windows()

def window_id():
	return sublime.active_window().id()

def currentView():
	if sublime.active_window():
		if sublime.active_window().active_view():
			return sublime.active_window().active_view()
	return None

def runWindowCommand(root_folder,commandname,args):
	for window in sublime.windows():
		if pathManager.root_folder(window) == root_folder:
			window.run_command(commandname,args)

def error(message):
	sublime.error_message(message)