import sublime
import sublime_plugin
import os

class Controls:
	def __init__(self,sublime_settings, file_name):

		self.auto_save         = sublime_settings.get('auto_save', False)
		self.whitelist 		   = [x.lower() for x in sublime_settings.get('whitelist_filetypes', []) or []]

		if self.auto_save:
			if not Controls.is_syntax_supported(self.whitelist, file_name):
				self.auto_save = False

	@staticmethod
	def is_syntax_supported(whitelist,full_filepath_with_name):

		filetype = Controls.path_to_fileextension(full_filepath_with_name)

		if len(whitelist) > 0 and filetype:
			for whitelisted_filetype in whitelist:
				if whitelisted_filetype == filetype:
					return True
			return False

		#fallback
		if filetype and filetype == ".md":
			return True

	@staticmethod
	def path_to_fileextension(full_filepath_with_name):
		return os.path.splitext(os.path.basename(full_filepath_with_name))[1]



class ViewAutosave(sublime_plugin.ViewEventListener):
	def __init__(self, view):

		self.view = view

		wiki_settings = sublime.load_settings('wiki.sublime-settings')
		self.settings = wiki_settings.get("saving")
		self.Pref = Controls(self.settings, self.view.file_name())

	def on_modified_async(self):

		if self.Pref and self.Pref.auto_save:
			print("saved")
			self.view.window().run_command("save")
		else:
			print("not saved")
