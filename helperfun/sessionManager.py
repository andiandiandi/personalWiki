
_sessions = {}

def add_session(window,db):
	session = Session(window,db)
	_sessions[window.window_id] = session


def remove_session(key,window=None):
	id = key
	if window:
		id = window.window_id
	del _sessions[id]


class Session:
	def __init__(self,window,db):
		self.window = window
		self.db = db