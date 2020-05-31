import os
import imp
from . import pathManager

imp.reload(pathManager)

__CONFIGFOLDERNAME = "wikiconfig"

class ConfigFile:
	success=0
	no_project=1
	no_config=2
	file_exists=3

	def __init__(self,state,path):
		self.state = state
		self.path = path

#returns ConfigFile
def parse_config(window):
	window_root = pathManager.root_folder_of(window)
	if not window_root:
		return ConfigFile(ConfigFile.no_project, None)

	wikiconfig = os.path.join(window_root,__CONFIGFOLDERNAME)
	config_exists = pathManager.exists(wikiconfig)
	if config_exists:
		return ConfigFile(ConfigFile.success, wikiconfig)

	return ConfigFile(ConfigFile.no_config, None)

#returns ConfigFile
def create_config():
	window_root = pathManager.root_folder_of_window()
	if not window_root:
		return ConfigFile(ConfigFile.no_project, None)

	wikiconfig = os.path.join(window_root,__CONFIGFOLDERNAME)
	try:
		os.mkdir(wikiconfig)
		return ConfigFile(ConfigFile.success, wikiconfig)
	except  FileExistsError:
		 return ConfigFile(ConfigFile.file_exists, wikiconfig)