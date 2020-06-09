import os
import time
import threading

from . import databaseManager
from . import pathManager


wikis = {}
_zombieCollector = None


############## session related #######################

def add_wiki(wiki):
	if not wiki.wikipath in wikis:
		wikis[wiki.wikipath] = wiki

	#if not _zombieCollector:
	#	run_zombieCollector()


def remove_wiki(wiki, wikipath=None):
	if wiki:
		del wikis[wiki.wikipath]
	else:
		del wikis[wikipath]

class Wiki:
	def __init__(self,wikipath, session,db = None):
		self.wikipath = wikipath
		self.session = session
		self.session['id'] = 'wikipath'
		self.db = db if db else None

	def has_session(self):
		if not session:
			return False
		if not session["id"]:
			return False
		return True

	def initialize_db(self):
		if not self.db:
			self.db = databaseManager.DbWrapper(self)
			self.db.create_connection()


############### threading section#################

def check_zombies_every_n_seconds():
	zombie_clear_interval = get_zombie_clear_interval()

	while wikis:
		current_sublime_open_windows = [window.window_id for window in sublimeApi.windows()]
		remove = [k for k in wikis.keys() if k not in current_sublime_open_windows]
		for k in remove: 
			remove_wiki(k)

		time.sleep(zombie_clear_interval)


def run_zombieCollector():
	global _zombieCollector
	_zombieCollector = threading.Thread(target=check_zombies_every_n_seconds, daemon=True)
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
