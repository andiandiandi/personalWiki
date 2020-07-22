import sublime

def windows():
	return sublime.windows()

def window_id():
	return sublime.active_window().id()

def currentView():
	if sublime.active_window():
		if sublime.active_window().active_view():
			return sublime.active_window().active_view()
	return None

def runWindowCommand(commandname,args):
	sublime.active_window().run_command(commandname,args)

def error(message):
	sublime.error_message(message)