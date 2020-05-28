import sublime
import sublime_plugin
import imp
from .helperfun import pathManager
from .helperfun import wikiValidator

def plugin_loaded():
	imp.reload(pathManager)
	imp.reload(wikiValidator)

class InitWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		view = self.view
		wiki_structure = self.project_checkup()

	def project_checkup(self):
		ValidationResult = wikiValidator.validate()
		if ValidationResult == wikiValidator.ValidationResult.success:
			#db
			print("db")
		elif ValidationResult == wikiValidator.ValidationResult.no_project:
			sublime.message_dialog("initialization not possible: no folder found")
		else:
			config_created = wikiValidator.create_config()
			if config_created:
				print("created config; db")
			else:
				sublime.message_dialog("""no 'wikiconfig' folder found;
									      could not initialize one either""")
