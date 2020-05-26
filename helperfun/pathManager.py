import os
import sublime

def dir_of_view(view):
	return os.path.split(view.file_name())[0]

def dir_of_current_view():
	return dir_of_view(sublime.active_window().active_view())

def basename_w_ext_of_path(full_filepath_with_name):
	temp = os.path.splitext(os.path.basename(full_filepath_with_name))
	return temp[0] + temp[1]

def extension_of_filepath(full_filepath_with_name):
	return os.path.splitext(os.path.basename(full_filepath_with_name))[1]

def root_folder_of_window(window):
	return sublime.active_window().extract_variables()['folder']

#top most root folder of the window that view sits in
def root_folder_of_view(view):
	return view.window().extract_variables()['folder'] 

#immediate folder of given view
def folder_of_view(view):
	return os.path.dirname(view.file_name())

def folder_has_file(folder,full_path_of_file):
	for folder, subs, files in os.walk(folder):
			for filename in files:
				if(filename == os.path.basename(full_path_of_file)):
					return True

def extract_fileextension(full_filepath_with_name):
	return os.path.splitext(os.path.basename(full_filepath_with_name))[1]

def path_to_helperfun():
	return os.path.dirname(__file__)

def file_exists(full_path_of_file):
	return os.path.isfile(full_path_of_file) 
	return os.path.isfile()

def resolve_relative_path(base_path,relative_navigation):
	unresolved_rel_path = os.path.join(base_path, relative_navigation)
	#points to root-folder of this plugin
	resolved_abs_path = os.path.realpath(unresolved_rel_path)

	return resolved_abs_path

def path_to_plugin_folder():
	return resolve_relative_path(path_to_helperfun(),"..")
