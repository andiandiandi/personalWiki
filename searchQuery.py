import sublime
import sublime_plugin
import json

import shlex
import imp

from .helperfun import sessionManager
from .helperfun import pathManager
from .helperfun import localApi

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)

class SearchFulltextCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			def on_done(searchQuery):
				print(searchQuery)
				con.searchQuery(searchQuery)
				#con.searchFulltext({"phrase":"haus nicht","linespan":10})

			def on_cancel():
				print("cancelled")

			localApi.window().show_input_panel("Wiki-Search", "", on_done, None,None)

def load_and_select(window, filename, begin, end):
	window = window or sublime.active_window()
	view = window.open_file(filename)
	if view.is_loading():
		view.settings().set("_do_select", [begin-1, end])
	else:
		view.run_command("select_in_view", {"begin": begin-1,"end": end})


class SelectInViewCommand(sublime_plugin.TextCommand):
	def run(self,edit,begin,end):
		view = self.view
		start_pos = view.text_point(begin, 0)
		end_pos = view.text_point(end, 0)
		view.sel().clear()
		view.sel().add(sublime.Region(start_pos, end_pos))


class ShowSearchResultCommand(sublime_plugin.TextCommand):
	def run(self,edit,data):
		try:
			print("DATA",data)
			if data:
				d = json.loads(data)

				c = """
					<html>
						<body>
							<style>
								a.fillthediv{display:block;height:100%;width:1000px;text-decoration: none;}
							</style>
						
				"""
				for entry in d:
					subHtml = """
							<div>
								<a href="{2}::{3}" class="fillthediv">
									{0}
									{1}
								</a>
							</div>
							
					""".format(("<p>rating:" + str(entry["rating"]) + "</p>") if "rating" in entry else "",("<p>" + entry["fullphrase"] + "</p>")
								 if "fullphrase" in entry else ("<p>" + entry["filepath"] + "::" + str(entry["lines"]) + "</p>"),
								entry["filepath"],entry["lines"] if "lines" in entry and entry["lines"] else [1])

					c += subHtml

				c += """
					</body>
				</html>
				"""

				def on_hide():
					pass

				def on_navigate(href):
					#if href == "closePopup":
					#	self.view.hide_popup()
					print(href)
					viewname,linesStr = href.split("::")
					lines = json.loads(linesStr)
					self.view.hide_popup()
					load_and_select(None,viewname,lines[0],lines[-1])

				self.view.show_popup(c,max_width=1000,max_height=1080,location=0,on_navigate=on_navigate,on_hide=on_hide)
		except Exception as E:
			localApi.error(str(E))



class SampleSampleListener(sublime_plugin.ViewEventListener):
	@classmethod
	def is_applicable(cls, settings):
		return settings.has("_do_select")

	def on_load(self):
		selRange = self.view.settings().get("_do_select")
		self.view.run_command("select_in_view", {"begin": selRange[0],"end": selRange[-1]})

		self.view.settings().erase("_do_select")

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
		else:
			localApi.error("connect to wiki server first")

	def on_change(self,a):
		pass
		
	def on_cancel(self):
		pass