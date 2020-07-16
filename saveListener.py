import sublime
import sublime_plugin
import imp


from .helperfun import sessionManager
from .helperfun import pathManager
imp.reload(sessionManager)
imp.reload(pathManager)

class SaveListener(sublime_plugin.EventListener):
	def on_post_save_async(self,view):
		root_folder = pathManager.root_folder()
		con = sessionManager.connection(root_folder)
		if con and con.isConnected():
			jsonfile = pathManager.createFile(view.file_name())
			con.save(jsonfile)