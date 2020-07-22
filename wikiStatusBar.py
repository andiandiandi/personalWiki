import sublime
import sublime_plugin
import imp

from .helperfun import sessionManager
from .helperfun import pathManager

imp.reload(sessionManager)
imp.reload(pathManager)


class UpdateWikiStatusCommand(sublime_plugin.WindowCommand):
	def run(self, status):
		window = self.window
		views = window.views()
		for view in views:
			if status != "removed":
				setStatus(view,status)
			else:
				eraseStatus(view)				
			

class WikiStatusBar(sublime_plugin.ViewEventListener):

	def on_activated_async(self):
		view = self.view
		root_folder = pathManager.root_folder_of_view(view)

		if sessionManager.hasProject(root_folder):
			connection = sessionManager.connection(root_folder)
			print(type(connection.wikiState))
			print(connection.wikiState)
			setStatus(view,connection.wikiState)

def setStatus(view,message):
	view.set_status("personalwikiplugin","Wiki: {0}".format(message))

def eraseStatus(view):
	view.erase_status("personalwikiplugin")
