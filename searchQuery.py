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
	def run(self, edit, d = None):
		if not d:
			root_folder = pathManager.root_folder()
			if sessionManager.hasProject(root_folder):
				con = sessionManager.connection(root_folder)
				con.savedSearchQuery()
		else:
			try:
				data = json.loads(d)
				c = """
					<html>
						<body>
							<style>
								a.fillthediv{display:block;height:100%;width:1000px;text-decoration: none;}
							</style>
							
					"""
				for entry in data:
					c += """
										<div>
											<a href="{0}" class="fillthediv">
												<p>{0}</p>
												<p><a href="{0} -d">delete</a></p>
											</a>
										</div>
										
								""".format(entry["rawString"])

				def on_navigate(href):
					sublime.active_window().run_command("search_query",args={"searchQuery":href})

				self.view.show_popup(c,max_width=1000,max_height=1080,location=0,on_navigate=on_navigate,on_hide=None)
			except Exception as E:
				localApi.error(str(E))

class SearchQueryCommand(sublime_plugin.TextCommand):
	def run(self, edit, searchQuery = None):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			if searchQuery:
				con.searchQuery(searchQuery)
				return

			def on_done(searchQuery):
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
			print(queryResult)
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
						print("entry",entry)
						if entry["lines"]:
							for line in entry["lines"]:
								subHtml = """
										<div>
											<a href="{2}::{3}" class="fillthediv">
												<p>file:{0} | line:{1}</p>
												<p>> "{4}"</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),line,entry["filepath"],entry["lines"],entry["content"])

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
				elif searchType == "deleted":
					pass
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

				self.view.show_popup(c,max_width=650,max_height=1080,location=0,on_navigate=on_navigate,on_hide=on_hide)
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

class SearchQueryTestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		queryResult = json.dumps({"type": "fulltextsearch", "data": [{"lines": [3], "rating": 1.0, "fullphrase": "Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas", "filepath": "C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md"}]})
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
						print("entry",entry)
						if entry["lines"]:
							for line in entry["lines"]:
								subHtml = """
										<div>
											<a href="{2}::{3}" class="fillthediv">
												<p>file:{0} | line:{1}</p>
												<p>> "{4}"</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),line,entry["filepath"],entry["lines"],entry["content"])

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
				elif searchType == "deleted":
					pass
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

				self.view.show_popup(c,max_width=650,max_height=1080,location=0,on_navigate=on_navigate,on_hide=on_hide)
		except Exception as E:
			localApi.error(str(E))