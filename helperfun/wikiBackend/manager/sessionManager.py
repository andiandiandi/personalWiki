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

class Wiki:
	def __init__(self,sid, db = None):
		self.sid = sid
		self.db = db if db else None

	def initialize_db(self):
		if not self.db:
			self.db = databaseManager.DbWrapper(self)
			self.db.create_connection()


################## cleanup #####################
def clean_up():
	wikis = None
