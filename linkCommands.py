import sublime
import sublime_plugin
import os
import imp

import json

from .helperfun import sessionManager
from .helperfun import pathManager

imp.reload(sessionManager)
imp.reload(pathManager)


def plugin_loaded():
	pass


class CreateImagelinkCommand(sublime_plugin.TextCommand):
	def run(self, edit, files = None):
		if files:
			def on_done(index):
				if index < 0 :
					return
				else:
					file = files[index]
					title = file["title"]
					link = file["link"]
					self.createImagelink(edit,title=title,link=link)
			self.view.show_popup_menu([f["tooltip"] for f in files], on_done)
		else:
			self.createImagelink(edit)
	def createImagelink(self,edit,title=None,link=None):
		self.view.replace(edit,self.view.sel()[0],"![{0}]({1})".format(title if title else '',link if link else ''))
		selectedRegion = self.view.sel()[0]
		a = selectedRegion.a+2
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(a,a))

class ShowWikilinkOptionsCommand(sublime_plugin.TextCommand):
	def run(self, edit, templates, folders, filename):
		if type(templates) == list and type(folders) == list and self.view:
			root_folder = pathManager.root_folder()
			if sessionManager.hasProject(root_folder):
				con = sessionManager.connection(root_folder)
				def on_doneTemplates(index):
						if index < 0:
							return
						if index == 0:
							template = None
						else:
							template = templates[index]
						
						def on_doneFolders(index):
							if index < 0:
								return
							if index == 0:
								def on_doneInput(input):
									d = {"type":"create",
										"template":template,
										"folder":input,
										"filename":filename,
										"srcPath":self.view.file_name()}
									con.createWikilink(d)
								def on_cancelInput():
									return
								sublime.active_window().show_input_panel("folder to create", os.path.dirname(self.view.file_name()), on_doneInput, None, on_cancelInput)
							else:
								folder = folders[index]
								d = {"type":"create",
										"template":template,
										"folder":folder,
										"filename":filename,
										"srcPath":self.view.file_name()}
								con.createWikilink(d)

						folders.insert(0,"+new folder")
						self.view.show_popup_menu(folders, on_doneFolders)

				templates.insert(0,"-no Template")
				self.view.show_popup_menu(templates, on_doneTemplates)

class CreateWikilinkCommand(sublime_plugin.TextCommand):
	def run(self, edit, files):
		if type(files) == list:
			if len(files) > 1:
				def on_done(index):
					if index < 0:
						return
					file = files[index]
					title = file["title"] 
					link = file["link"]
					self.view.replace(edit,self.view.sel()[0],"[{0}]({1})".format(title,link))

				self.view.show_popup_menu([f["tooltip"] for f in files], on_done)
			else:
				file = files[0]
				title = file["title"]
				link = file["link"]
				sel = self.view.sel()
				self.view.replace(edit,self.view.sel()[0],"[{0}]({1})".format(title,link))


class ToggleWikilinkCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			if self.view:
				view = self.view
				selected_region = None

				word = self.selectWord(view)
				if word:
					d = {"type":"toggle",
						"word":word,
						"srcPath":view.file_name()}
					con.createWikilink(d)
				else:
					d = {"type":"imagelink",
					   "srcPath":view.file_name()}
					con.createWikilink(d)

	def selectWord(self,view):
		for region in view.sel():
			if not region.empty():
				# Get the selected text
				selected_region = region
				selected_wikiword = view.substr(region)
			else:
				#automatically select current word at cursor
				current_caret_pos = view.sel()[0]
				view.run_command("expand_selection", {"to": "word"}) 
				expanded_selection = view.sel()[0]
				selected_region = sublime.Region(expanded_selection.begin(),expanded_selection.end())
				selected_wikiword = view.substr(selected_region)
				if len(selected_wikiword) == 0 or selected_wikiword.isspace():
					view.sel().clear() 
					view.sel().add(sublime.Region(current_caret_pos.end()))
					return

		if selected_region:
			return view.substr(selected_region)

		return None