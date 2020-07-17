import sublime
import sublime_plugin
import json

import imp

from .helperfun import sessionManager
from .helperfun import pathManager
imp.reload(sessionManager)
imp.reload(pathManager)

class SearchQueryDebugCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel("enter name", "testfile", self.on_done, self.on_change, self.on_cancel)

	def on_done(self,a):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			jsonsearch = {"files":{"negate":False,"values":[a + ".md"]},"element":{"negate":False, "value":"headers"},"values":[]}
			jsonsearch2 = {"files":{"negate":False,"values":["subtestfile.md"]},"element":{"negate":False, "value":"headers"},"values":[]}

			con.searchQuery(jsonsearch)

	def on_change(self,a):
		pass
		
	def on_cancel(self):
		pass
		
class OpenViewAtLineCommand(sublime_plugin.TextCommand):

	viewname = None
	line = None
	def run(self, edit, viewname, line):
		# Convert from 1 based to a 0 based line number
		if sublime.active_window().active_view().file_name() == viewname:
			view = self.view
			line = int(line) - 1

			# Negative line numbers count from the end of the buffer
			if line < 0:
				lines, _ = view.rowcol(view.size())
				line = lines + line + 1

			pt = view.text_point(line, 0)

			view.sel().clear()
			view.sel().add(sublime.Region(pt))

			view.show(pt)
		else:
			OpenViewAtLineCommand.viewname = viewname
			OpenViewAtLineCommand.line = line
			sublime.active_window().open_file(viewname)
		


class ViewOnloadListener(sublime_plugin.ViewEventListener):
	def on_load(self):
		view = self.view
		if OpenViewAtLineCommand.viewname and OpenViewAtLineCommand.viewname == view.file_name():
			line = int(OpenViewAtLineCommand.line) - 1

			# Negative line numbers count from the end of the buffer
			if line < 0:
				lines, _ = view.rowcol(view.size())
				line = lines + line + 1

			pt = view.text_point(line, 0)

			view.sel().clear()
			view.sel().add(sublime.Region(pt))

			view.show(pt)

			OpenViewAtLineCommand.viewname = None
			OpenViewAtLineCommand.line = None