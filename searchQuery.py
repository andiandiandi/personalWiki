import sublime
import sublime_plugin
import json
import os

import shlex
import imp

from .helperfun import sessionManager
from .helperfun import pathManager
from .helperfun import localApi

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)

class SavedSearchQueryCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)
			con.savedSearchQuery()

class SearchQueryCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			def on_done(searchQuery):
				print(searchQuery)
				con.searchQuery(searchQuery)


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
	def run(self,edit,queryResult):
		try:
			queryResultParsed = json.loads(queryResult)
			searchType = queryResultParsed["type"]
			data = queryResultParsed["data"]
			if data:
				c = """
					<html>
						<body>
							<style>
								a.fillthediv{display:block;height:100%;width:1000px;text-decoration: none;}
							</style>
							
					"""
				if searchType == "tagsearch":
					for entry in data:
						if entry["lines"]:
							for line in entry["lines"]:
								subHtml = """
										<div>
											<a href="{2}::{3}" class="fillthediv">
												<p>file:{0} | line:{1}</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),line,entry["filepath"],entry["lines"])

								c += subHtml
						else:
							subHtml = """
										<div>
											<a href="{1}::{2}" class="fillthediv">
												<p>file: {0}</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),entry["filepath"],[0])
								
							c += subHtml



				elif searchType == "fulltextsearch":
					for entry in data:
						subHtml = """
								<div>
									<a href="{2}::{3}" class="fillthediv">
										<p>rating: {0} | file: {5} | lines: {4}</p>
										<p>{1}</p>
									</a>
								</div>
								
						""".format(str(round((float(entry["rating"]) * 100),2)) + "%",entry["fullphrase"],
									entry["filepath"],entry["lines"],entry["lines"][0] if len(entry["lines"]) == 1 else str(entry["lines"][0]) + "-" + str(entry["lines"][-1]),
									os.path.basename(entry["filepath"]))

						c += subHtml
				else:
					localApi.error("unsupported query result: " + queryResult)
					return

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