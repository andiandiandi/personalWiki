import sublime
import os


template_keywords = {"$pagename","$creationdate"}

def list_available_templates():

	templates_folder = get_templates_folder()
	templates_list = []

	for folder, subs, files in os.walk(templates_folder):
			for filename in files:
				if(filename.endswith('.md')):
					filename_without_ext = os.path.splitext(os.path.basename(filename))[0]
					templates_list.append(filename_without_ext)

	return templates_list

def get_templates_folder():

	return os.path.dirname(os.path.realpath(__file__))


