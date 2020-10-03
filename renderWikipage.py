import sublime_plugin,sublime
import imp

import webbrowser

from .helperfun import pathManager
from .helperfun import sessionManager

from requests.utils import quote

imp.reload(pathManager)

class RenderWikipageCommand(sublime_plugin.TextCommand):
	def run(self, edit, path = None):
		root_folder = pathManager.root_folder()

		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			if path:
				sid = con.sid()
				encodedPath = quote(path, safe='')

				webbrowser.open("http://localhost:9000/{}/{}"
						.format(sid,encodedPath))
			else:
				view = self.view
				path = view.file_name()
				con.renderWikipage(path)
