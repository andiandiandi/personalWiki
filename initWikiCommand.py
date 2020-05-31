import sublime
import sublime_plugin
import imp
from .helperfun import wikiManager

def plugin_loaded():
	imp.reload(wikiManager)


def plugin_unloaded():
	wikiManager.clean_up()
		

class DebugInitCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		wikiManager.debug()

class InitWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		window = self.view.window()
		init_successful = wikiManager.initWikiProject(window)

		if not init_successful:
			sublime.message_dialog("Initializing Wiki did not succeed")
