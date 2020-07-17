import sublime

def windows():
	return sublime.windows()

def window_id():
	return sublime.active_window().id()

def error(message):
	sublime.error_message(message)