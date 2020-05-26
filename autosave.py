import sublime
import sublime_plugin
import imp
import time
import threading
from .helperfun import wikiSettingsManager
from .helperfun import pathManager

def plugin_loaded():
	imp.reload(pathManager)
	imp.reload(wikiSettingsManager)
	global Controls
	Controls = Controls()

	global Thread
	Thread = threading.Thread(target=print_every_n_seconds, daemon=True)
	Thread.start()

IntervalTaskRunner = None
Thread = None
Controls = None

def save_every_n_seconds():
	saved_unique_num = Controls.dynamic_unique_num
	while saved_unique_num == Controls.dynamic_unique_num:
		if Controls and Controls.auto_save:
			current_active_view = sublime.active_window().active_view()
			if Controls.is_filetype_supported(current_active_view.file_name()):
				print("saved")
				current_active_view.window().run_command("save")
		else:
			print("not saved")
			return
		time.sleep(Controls.saving_interval)


class Controls:
	def __init__(self):

		sublime_settings 	    = wikiSettingsManager.get("saving")

		self.auto_save          = sublime_settings.get('auto_save', False)
		self.whitelist 		    = [x.lower() for x in sublime_settings.get('whitelist_filetypes', []) or []]
		self.saving_interval    = sublime_settings.get('saving_interval', 25)
		self.dynamic_unique_num = int(round(time.time() * 1000))

		#only unsigned integers for saving-interval
		if self.saving_interval <= 0:
			self.saving_interval = 25

	def is_filetype_supported(self,full_filepath_with_name):

		filetype = pathManager.extension_of_filepath(full_filepath_with_name)

		if len(self.whitelist) > 0 and filetype:
			for whitelisted_filetype in self.whitelist:
				if whitelisted_filetype == filetype:
					return True
			return False

		#fallback
		if filetype and filetype == ".md":
			return True
		