import sublime
import sublime_plugin
import os
import time
import datetime
from .wikipageTemplates import templateGenerator as templateGenerator
import imp

def plugin_loaded():
    imp.reload(templateGenerator)

class InsertTemplateCommand(sublime_plugin.TextCommand):
	def run(self, edit, wikipage = None, template_filename=None):
		if not (wikipage or template_filename):
			sublime.error_message("could not insert template text: file-reference or template could not be found")
		else:
			self.wikipage = wikipage
			self.template_filename = template_filename
			if os.path.isfile(wikipage): 
				template_text = self.generate_template_text()
				if template_text:
					with open(wikipage, 'w') as file_to_edit:
						file_to_edit.write(template_text)

	def generate_template_text(self):
		templates_folder = self.get_templates_folder()
		full_template_file_name = templates_folder + "\\" + self.template_filename + ".md"
		if os.path.isfile(full_template_file_name): 
			with open(full_template_file_name, 'r') as file_to_edit:
				file_buffer = file_to_edit.read()

		if file_buffer:
			for keyword in templateGenerator.template_keywords:
				if keyword in file_buffer:
					file_buffer = file_buffer.replace(keyword,self.generate_replacement(keyword))
			return file_buffer
		else:
			return "created at {0}".format(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))

	def get_templates_folder(self):
		return os.path.dirname(os.path.realpath(__file__)) + "\\wikipageTemplates"

	def generate_replacement(self,keyword):
		if keyword == "$pagename":
			return os.path.splitext(os.path.basename(self.wikipage))[0]
		elif keyword == "$creationdate":
			return datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

		return ""