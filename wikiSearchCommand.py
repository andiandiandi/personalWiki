import sublime_plugin,sublime

class WikiSearchCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.open_file("testfile2.md", sublime.TRANSIENT)
		b = view.substr(sublime.Region(0, view.size()))
		print(b)