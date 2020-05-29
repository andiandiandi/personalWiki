import sublime
import sublime_plugin
import imp
from .helperfun import wikiSettingsManager
from .helperfun import pathManager
from .helperfun import wikiValidator
from .helperfun import databaseManager
from .helperfun import sessionManager
import time
import threading

def plugin_loaded():
	imp.reload(wikiSettingsManager)
	imp.reload(pathManager)
	imp.reload(wikiValidator)
	imp.reload(databaseManager)
	imp.reload(sessionManager)

	global Controls
	Controls = Controls()

	global Thread
	global pill2kill
	pill2kill = threading.Event()
	Thread = threading.Thread(target=clear_sessions_every_n_seconds, args=(pill2kill,), daemon=True)
	Thread.start()

def plugin_unloaded():
	global Thread
	global pill2kill
	pill2kill.set()
	Thread.join()

pill2kill = None
Thread = None
Controls = None

def clear_sessions_every_n_seconds(stop_event):
	while not stop_event.wait(1):
		current_sublime_open_windows = [window.window_id for window in sublime.windows()]
		remove = [k for k in sessionManager._sessions.keys() if k not in current_sublime_open_windows]
		for k in remove: del sessionManager._sessions[k]

		time.sleep(Controls.clear_sessions_interval)

class Controls:
	def __init__(self):

		sublime_settings 	    = wikiSettingsManager.get("session")

		self.clear_sessions_interval    = sublime_settings.get('clear_sessions_interval', 25)

		#only unsigned integers for saving-interval
		if self.clear_sessions_interval <= 0:
			self.clear_sessions_interval = 25
		

class DebugInitCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		print(sessionManager._sessions)

class InitWikiCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.project_checkup()


	def project_checkup(self):

		ValidationResult = wikiValidator.validate()
		if ValidationResult[0] == wikiValidator.ValidationResult.success:
			window = self.view.window()
			db = databaseManager.Db()
			
			sessionManager.add_session(window,db)

			dbValidationResult = databaseManager.db_existance_check()
			if dbValidationResult[0] == wikiValidator.ValidationResult.success:
				print("db exists")
			elif dbValidationResult[0] == wikiValidator.ValidationResult.failure:
				print("no db found")
			else:
				sublime.message_dialog("could not create db")

		elif ValidationResult[0] == wikiValidator.ValidationResult.no_project:
			sublime.message_dialog("initialization not possible: no folder found")
		else:
			config_created = wikiValidator.create_config()
			if config_created:
				dbValidationResult = databaseManager.db_existance_check()
				if dbValidationResult[0] > 0:
					sublime.message_dialog("could not create db")

			else:
				sublime.message_dialog("""no 'wikiconfig' folder found;
									      could not initialize one either""")