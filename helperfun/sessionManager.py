from . import pathManager
from . import wikiSettingsManager
import sublime
import imp
import os
import time
import threading

imp.reload(pathManager)
imp.reload(wikiSettingsManager)


wikis = {}

_zombieCollector = None


############## session related #######################

def add_wiki(window,db,configpath,Wiki_obj = None):
	if Wiki_obj:
		wikis[Wiki.window.window_id] = Wiki_obj
	else:
		wiki = Wiki(window,db,configpath)
		wikis[window.window_id] = wiki

	if not _zombieCollector:
		run_zombieCollector()


def remove_wiki(key,window=None):
	if window:
		del wikis[window.window_id]
	else:
		del wikis[key]

def current_wiki():
	return wikis[sublime.active_window().window_id]

class Wiki:
	def __init__(self,window,db,configpath):
		self.window = window
		self.db = db
		self.configpath = configpath
		self.wikipath = pathManager.resolve_relative_path(configpath,"..")

	def wikiname(self):
		return os.path.basename(self.wikipath)



############### zombie collection #################

def check_zombies_every_n_seconds(stop_event):
	zombie_clear_interval = get_zombie_clear_interval()
	while wikis:

		current_sublime_open_windows = [window.window_id for window in sublime.windows()]
		remove = [k for k in wikis.keys() if k not in current_sublime_open_windows]
		print(wikis)
		print(remove)
		for k in remove: 
			remove_wiki(k)

		time.sleep(zombie_clear_interval)



def run_zombieCollector():
	global pill2kill
	pill2kill = threading.Event()

	global _zombieCollector
	_zombieCollector = threading.Thread(target=check_zombies_every_n_seconds, args=(pill2kill,), daemon=True)
	_zombieCollector.start()

def stop_zombieCollector():
	global _zombieCollector
	if not _zombieCollector:
		return

	_zombieCollector.join()


def get_zombie_clear_interval():
	sublime_settings 	    = wikiSettingsManager.get("session")
	clear_sessions_interval    = sublime_settings.get('clear_sessions_interval', 25)

	#only unsigned integers for saving-interval
	if clear_sessions_interval <= 0:
		clear_sessions_interval = 25

	return clear_sessions_interval

################## cleanup #####################
def clean_up():
	wikis = None
