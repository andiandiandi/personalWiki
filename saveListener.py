import sublime
import sublime_plugin
import imp


from .helperfun import sessionManager
from .helperfun import pathManager
imp.reload(sessionManager)
imp.reload(pathManager)

class SaveListener(sublime_plugin.ViewEventListener):

	def __init__(self,view):
		super(SaveListener,self).__init__(view)
		self.modified = False

	def on_post_save_async(self):
		#SaveListener.saveFile(self.view.file_name())
		self.modified = False


	def on_deactivated(self):
		return
		if self.modified:
			#SaveListener.saveFile(self.view.file_name())
			self.view.run_command("save")
			self.modified = False


	def on_modified(self):
		if not self.modified:
			self.modified = True

	@staticmethod
	def saveFile(filepath):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)
			if con and con.isConnected():
				jsonfile = pathManager.createFile(filepath)
				con.save(jsonfile)
