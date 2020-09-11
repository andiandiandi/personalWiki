import sublime_plugin,sublime
from threading import Timer
import io
import imp
import os
from .helperfun import pathManager

def plugin_loaded():
	global DragNDropManager
	DragNDropManager = DragNDropManager()
	imp.reload(pathManager)

class DragNDropState:
	ready = 0
	listening = 1

class DragNDropManager():
	def __init__(self):
		self.state = DragNDropState.ready
		self.TIME_TO_RUN = 5
		self.timer = None
		self.dir_to_save_to = None
		self.opened_files = []

	def __exit__(self, exc_type, exc_value, traceback):
		if self.timer:
			if timer.is_alive():
				timer.cancel()

	def listen(self):
		self.timer = Timer(self.TIME_TO_RUN,self.__timeout)
		self.dir_to_save_to = pathManager.dir_of_current_view()
		self.timer.start()
		self.opened_files = [pathManager.basename_w_ext_of_path(v.file_name()) for v in sublime.active_window().views()]
		print("timer started")
		self.__changeState(DragNDropState.listening)

	def ready(self):
		if self.timer and self.timer.is_alive():
				self.timer.cancel()
		self.timer = None
		self.dir_to_save_to = None
		self.opened_files = []
		print("timer reset")
		self.__changeState(DragNDropState.ready)

	def save_file(self,filename_to_copy,view_buffer):
		targetpath = os.path.join(self.dir_to_save_to,filename_to_copy)
		with io.open(targetpath, "w",encoding="utf-8") as file:
			file.write(str(view_buffer))
		self.ready()
		return targetpath

	def is_ready(self):
		return self.state == DragNDropState.ready

	def is_listening(self):
		return self.state == DragNDropState.listening

	def __timeout(self):
		self.ready()

	def __changeState(self,new_state):
		self.state = new_state


class DragAndDropCommand(sublime_plugin.TextCommand):
	def run(self,edit,filename_dropped_file = None):
		if DragNDropManager.is_ready():
			DragNDropManager.listen()
		elif DragNDropManager.is_listening():
			if filename_dropped_file:
				view = sublime.active_window().find_open_file(filename_dropped_file)
				view_buffer = view.substr(sublime.Region(0, view.size()))

				dropped_file_name = view.file_name()
				basename_dropped_file = os.path.basename(dropped_file_name)
				print("BASE",dropped_file_name)
				
				targetpath = DragNDropManager.save_file(basename_dropped_file,view_buffer)
				print("TARGETPATH",targetpath)
				#close new view that opens when u drag a file into window
				sublime.active_window().run_command('close_file')
				current_filename = sublime.active_window().active_view().file_name()
				print("CURRENT",current_filename)
				sublime.active_window().active_view().run_command("create_wikilink",
					{"files":[{"title":basename_dropped_file.split(".")[0],"link":os.path.relpath(targetpath,os.path.dirname(current_filename))}]})
			

class DragNDropListener(sublime_plugin.EventListener):

	def on_load(self,view):
		global DragNDropManager
		if DragNDropManager.is_listening():
			basename_dropped_file = os.path.basename(view.file_name())
			for opened_file in DragNDropManager.opened_files:
					if basename_dropped_file == opened_file:
						sublime.active_window().run_command('close_file')
						return

			#check if dropped file already exists in wikifolder of current page
			if pathManager.exists(os.path.join(DragNDropManager.dir_to_save_to,os.path.basename(view.file_name()))):
				sublime.active_window().run_command('close_file')
				return

			#copy content of dragged file to new file with same name in dir of current view
			sublime.active_window().run_command("drag_and_drop",{"filename_dropped_file":view.file_name()})
			