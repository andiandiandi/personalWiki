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
		con = sessionManager.connection(root_folder)

		jsonsearch = {"files":{"negate":False,"values":[a + ".md"]},"element":{"negate":False, "value":"headers"},"values":[]}
		jsonsearch2 = {"files":{"negate":False,"values":["subtestfile.md"]},"element":{"negate":False, "value":"headers"},"values":[]}

		con.searchQuery(jsonsearch)

	def on_change(self,a):
		pass
		
	def on_cancel(self):
		print("canceled")
		
class GotoLineCommand(sublime_plugin.TextCommand):

    def run(self, edit, line):
        # Convert from 1 based to a 0 based line number
        line = int(line) - 1

        # Negative line numbers count from the end of the buffer
        if line < 0:
            lines, _ = self.view.rowcol(self.view.size())
            line = lines + line + 1

        pt = self.view.text_point(line, 0)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(pt))

        self.view.show(pt)
