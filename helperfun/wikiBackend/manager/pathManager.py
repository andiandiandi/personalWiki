import os

def basename_w_ext_of_path(full_filepath_with_name):
	temp = os.path.splitext(os.path.basename(full_filepath_with_name))
	return temp[0] + temp[1]

def extension_of_filepath(full_filepath_with_name):
	return os.path.splitext(os.path.basename(full_filepath_with_name))[1]


def folder_has_file(folder,full_path_of_file):
	for folder, subs, files in os.walk(folder):
			for filename in files:
				if(filename == os.path.basename(full_path_of_file)):
					return True

def extract_fileextension(full_filepath_with_name):
	return os.path.splitext(os.path.basename(full_filepath_with_name))[1]

def path_to_helperfun():
	return os.path.dirname(__file__)

def exists(full_path_of_file):
	return os.path.exists(full_path_of_file) 

def resolve_relative_path(base_path,relative_navigation):
	unresolved_rel_path = os.path.join(base_path, relative_navigation)
	#points to root-folder of this plugin
	resolved_abs_path = os.path.realpath(unresolved_rel_path)

	return resolved_abs_path

def filename(path):
	base = os.path.basename(path)
	return os.path.splitext(base)[0]
		
def extension(path):
	base = os.path.basename(path)
	return os.path.splitext(base)[1]

def relpath(path):
	return os.path.dirname(path)


def path_to_plugin_folder():
	return resolve_relative_path(path_to_helperfun(),"..")

def createFile(full_path):
	d = {}
	d["path"] = full_path
	d["content"] = open(full_path, 'r', encoding='utf8').read()
	d["lastmodified"] = os.path.getmtime(full_path)
	return d

def isFile(path,extension=None):
	if extension:
		return os.path.isfile(path) and extension == extension_of_filepath(path)
	return os.path.isfile(path) 

def path_to_dict(path):
	d = None
	if os.path.isdir(path):
		if os.path.basename(path) != "wikiconfig":
			d = {'name': os.path.basename(path)}
			d['type'] = "folder"
			directFolders = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path) if os.path.isdir(os.path.join(path,x))]
			d['folders'] = []
			for folder in directFolders:
				if folder:
					d['folders'].append(folder)
			d['files'] = [createFile(os.path.join(path,f)) for f in os.listdir(path) if isFile(os.path.join(path, f),extension=".md")]
	return d

