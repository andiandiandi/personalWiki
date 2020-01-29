import sublime
import sublime_plugin
import re
import os
import imp
from .wikipageTemplates import templateGenerator as templateGenerator

def plugin_loaded():
	imp.reload(templateGenerator)

class CheckForBrokenLinksCommand(sublime_plugin.TextCommand):
	def run(self, edit, also_check_http=False):
		#self.check_for_broken_local_references()
		templateGenerator.generate_template_text("timeAndPagename")

	def check_for_broken_local_references(self):
		root_folder = self.get_root_folder(self.view)

		for folder, subs, files in os.walk(root_folder):
			for filename in files:
				if(filename.endswith('.md')):
					with open(os.path.join(folder,filename), 'r') as file_to_read:
						read_buffer = file_to_read.read()
						r = sublime.Region()
						match_local_links = re.findall("[^!]\[.+\]\(.+\)",read_buffer)
						if match_local_links:
							for match in match_local_links:
								with_parentheses = re.search("\(.+\)",match).group(0)
								filename_w_extension = with_parentheses[1 : len(with_parentheses)-1]
								name = os.path.splitext(os.path.basename(filename_w_extension))[0] +  os.path.splitext(os.path.basename(filename_w_extension))[1]

	def get_root_folder(self,view):
		return view.window().extract_variables()['folder']