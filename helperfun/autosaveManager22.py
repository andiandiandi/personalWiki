import imp
import time
import threading
from . import wikiSettingsManager
from . import pathManager
from .api import sublimeApi

imp.reload(pathManager)
imp.reload(wikiSettingsManager)
imp.reload(sublimeApi)

_autosaveThread = None
_Controls = None
_shouldRun = False

def save_every_n_seconds():
	while _shouldRun:
		if _Controls and _Controls.auto_save:
			current_active_view = sublimeApi.active_window().active_view()
			if current_active_view and current_active_view.file_name():
				if _Controls.is_filetype_supported(current_active_view.file_name()):
					#print("saved")
					sublimeApi.run_window_command("save")
		else:
			#print("not saved")
			return
		time.sleep(_Controls.saving_interval)


def run_autosaveThread():
	global _autosaveThread
	global _shouldRun

	_shouldRun = True
	_autosaveThread = threading.Thread(target=save_every_n_seconds, daemon=True)
	_autosaveThread.start()

def stop_autosaveThread():
	global _autosaveThread
	if not _autosaveThread:
		return

	global _shouldRun

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

_Controls = Controls()

################## cleanup #####################
def clean_up():
 	stop_autosaveThread()



		