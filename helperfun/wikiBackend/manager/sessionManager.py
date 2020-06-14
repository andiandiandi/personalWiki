import os
import time
import threading

from . import databaseManager
from . import pathManager


wikis = {}
_zombieCollector = None


############## session related #######################

def add_wiki(wiki):
	if not wiki.sid in wikis:
		wikis[wiki.sid] = wiki

def remove_wiki(wiki, sid=None):
	if wiki:
		del wikis[wiki.sid]
	else:
		del wikis[sid]

def wiki(sid):
	if wikis[sid]:
		return wikis[sid]
	else:
		return None

class Wiki:
	def __init__(self,sid, db = None):
		self.sid = sid
		self.db = db if db else None

	def initialize_db(self, json_project_structure):
		if not self.db:
			self.db = databaseManager.DbWrapper(self)
			self.db.create_connection()
		self.db.initialize(json_project_structure)


################## cleanup #####################
def clean_up():
	wikis = None
