import sublime
import sublime_plugin

import imp
from .helperfun import sessionManager
from .helperfun import pathManager

imp.reload(sessionManager)
imp.reload(pathManager)


class WordCountCommand(sublime_plugin.TextCommand):
	
	def run(self,edit,searchWholeNotebook=False):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)
			if searchWholeNotebook:
				print("ALL")
				con.wordCount()
			else:
				print("single")
				if self.view:
					filepath = self.view.file_name()
					if filepath:
						con.wordCount(path=filepath)

class ShowWordCountCommand(sublime_plugin.TextCommand):
	def run(self,edit,d):
		sublime.message_dialog(d)


"""
import sublime, sublime_plugin, re
import threading
from math import ceil as ceil
from os.path import basename
import inspect
import os
import imp

from .helperfun import pathManager
from .helperfun import sessionManager

imp.reload(sessionManager)
imp.reload(pathManager)


def plugin_loaded():
	pass
	
class Controls:
	def __init__(self,sublime_settings, should_scan_whole_project):

		self.elapsed_time           = 0.4
		self.running                = False

		self.wrdRx                  = re.compile(sublime_settings.get('word_regexp', "^[^\w]?`*\w+[^\w]*$"), re.U)
		self.wrdRx                  = self.wrdRx.match
		self.splitRx                = sublime_settings.get('word_split', None)
		if self.splitRx:
			self.splitRx            = re.compile(self.splitRx, re.U)
			self.splitRx            = self.splitRx.findall

		self.enable_live_count      = sublime_settings.get('enable_live_count', True)
		self.enable_readtime        = sublime_settings.get('enable_readtime', False)
		self.enable_line_word_count = False if should_scan_whole_project else sublime_settings.get('enable_line_word_count', False)
		self.enable_line_char_count = False if should_scan_whole_project else sublime_settings.get('enable_line_char_count', False)
		self.enable_count_lines     = sublime_settings.get('enable_count_lines', False)
		self.enable_count_chars     = sublime_settings.get('enable_count_chars', False)
		self.enable_count_pages     = sublime_settings.get('enable_count_pages', True)

		self.words_per_page         = sublime_settings.get('words_per_page', 300)
		self.page_count_mode_count_words = sublime_settings.get('page_count_mode_count_words', True)
		self.char_ignore_whitespace = sublime_settings.get('char_ignore_whitespace', True)
		self.readtime_wpm           = sublime_settings.get('readtime_wpm', 200)
		self.whitelist              = [x.lower() for x in sublime_settings.get('whitelist_filetypes', []) or []]


class ShowWordcountCommand(sublime_plugin.TextCommand):

	def run(self,edit, should_scan_whole_project = True):

		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)
			if not con.isConnected():
				return

		self.should_scan_whole_project = should_scan_whole_project

		wiki_settings = sublime.load_settings('wiki.sublime-settings')
		self.settings = wiki_settings.get("wordcount")

		if should_scan_whole_project:
			self.start_scanning_whole_project()
		else:
			self.start_scanning_current_view()

		
	def start_scanning_whole_project(self):

		self.Pref = Controls(self.settings,self.should_scan_whole_project)

		view = self.view

		approved = None
		for open_view in view.window().views():
			if open_view.is_dirty():
				if not approved:
					approved = sublime.ok_cancel_dialog("found unsaved modified files in opened tabs, save and run wordcount?")
				if approved:
					open_view.run_command("save")
				else:
					return

		self.data_from_all_files = ""
		for folder, subs, files in os.walk(ShowWordcountCommand.get_root_folder(view)):
			for filename in files:
				if self.is_syntax_supported(filename):
					with open(os.path.join(folder,filename), 'r') as file_to_read:
						self.data_from_all_files += file_to_read.read()

		if len(self.data_from_all_files) < 10485760:
			WordCountThread(view, [self.data_from_all_files], None, False, self.Pref).start()


	@staticmethod
	def get_root_folder(view):
		return view.window().extract_variables()['folder']

	def start_scanning_current_view(self):
		
		view = self.view
		if not view.file_name():
			return

		self.Pref = Controls(self.settings,self.should_scan_whole_project)

		if self.is_syntax_supported(view.file_name()):
			sel = view.sel()
			if sel:
				if len(sel) == 1 and sel[0].empty():
					if not self.Pref.enable_live_count or view.size() > 10485760:
						print("view buffer too large")
					else:
						WordCountThread(view, [view.substr(sublime.Region(0, view.size()))], view.substr(view.line(view.sel()[0].end())), False, self.Pref).start()
				else:
					try:
						WordCountThread(view, [view.substr(sublime.Region(s.begin(), s.end())) for s in sel], view.substr(view.line(view.sel()[0].end())), True, self.Pref).start()
					except:
						pass
		else:
			sublime.error_message("filetype:'{0}' is currently not whitelisted\n|=>see WordCount.sublime-settings".format(self.filetype))


	def is_syntax_supported(self, full_filepath_with_name):

		#old way
		#vs =  view.settings()
		#self.syntax = vs.get('syntax')
		#self.syntax = basename(self.syntax).split('.')[0].lower() if self.syntax != None else "plain text"

		self.filetype = ShowWordcountCommand.path_to_fileextension(full_filepath_with_name)


		if len(self.Pref.whitelist) > 0 and self.filetype:
			for whitelisted_filetype in self.Pref.whitelist:
				if whitelisted_filetype == self.filetype:
					return True
			return False

		#fallback
		if self.filetype and self.filetype == ".md":
			return True


	@staticmethod
	def path_to_fileextension(full_filepath_with_name):
		print(full_filepath_with_name)
		return os.path.splitext(os.path.basename(full_filepath_with_name))[1]

class WordCountThread(threading.Thread):

	def __init__(self, view, content, content_line, on_selection,Pref):
		threading.Thread.__init__(self)
		self.view = view
		self.Pref = Pref
		self.content = content
		self.content_line = content_line
		self.on_selection = on_selection

		self.char_count = 0
		self.word_count_line = 0
		self.chars_in_line = 0

	def run(self):

		self.Pref.running         = True

		self.word_count      = sum([self.count(region) for region in self.content])

		if self.Pref.enable_count_chars:
			if self.Pref.char_ignore_whitespace:
				self.char_count  = sum([len(''.join(region.split())) for region in self.content])
			else:
				self.char_count  = sum([len(region) for region in self.content])

		if self.Pref.enable_line_word_count:
			self.word_count_line = self.count(self.content_line)

		if self.Pref.enable_line_char_count:
			if self.Pref.char_ignore_whitespace:
				self.chars_in_line = len(''.join(self.content_line.split()))
			else:
				self.chars_in_line = len(self.content_line)

		sublime.set_timeout(lambda:self.on_done(), 0)

	def on_done(self):

		readtime_min = int(self.word_count / self.Pref.readtime_wpm)
		readtime_sec = int(self.word_count % self.Pref.readtime_wpm / (self.Pref.readtime_wpm / 60))

		lines = (self.view.rowcol(self.view.size())[0] + 1)

		statistics_to_show = [
								  "words: {0}".format(self.word_count),
								  "chars: {0}".format(self.char_count),
								  "words in line: {0}".format(self.word_count_line),
								  "chars in line: {0}".format(self.chars_in_line),
								  "time to read({2}): {0} min, {1} sec".format(readtime_min,readtime_sec,"selected" if self.on_selection else "document"),
							 ]

		self.view.show_popup_menu(statistics_to_show,lambda index : None)

		 #todo
		#phantom_content = """
		#						<a href="close"><img src="{0}{1}" class="inlineImage" width="128" height="128"></a>
		#				  """.format(content_type,content_image)



"""
		nav = lambda href: hide_image(view,image_linkname)

		#self.view.add_phantom(image_linkname,region ,phantom_content,sublime.LAYOUT_BELOW, on_navigate = nav)


		self.Pref.running = False

	def count(self, content):

		wrdRx = self.Pref.wrdRx
		splitRx = self.Pref.splitRx
		if splitRx:
			words = len([1 for x in splitRx(content) if False == x.isdigit() and wrdRx(x)])
		else:
			words = len([1 for x in content.replace("'", '').replace('—', ' ').replace('–', ' ').replace('-', ' ').split() if False == x.isdigit() and wrdRx(x)])


		return words
"""
