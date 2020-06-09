import os
from . import pathManager

__CONFIGFOLDERNAME = "wikiconfig"

class ConfigFile:
	success=0
	no_config=2
	file_exists=3

	def __init__(self,state,path):
		self.state = state
		self.path = path

#returns ConfigFile
def parse_config(wikipath):

	wikiconfig = os.path.join(wikipath,__CONFIGFOLDERNAME)
	config_exists = pathManager.exists(wikiconfig)
	if config_exists:
		return ConfigFile(ConfigFile.success, wikiconfig)

	return ConfigFile(ConfigFile.no_config, None)

#returns ConfigFile
def create_config(wikipath):

	wikiconfig = os.path.join(wikipath,__CONFIGFOLDERNAME)
	try:
		os.mkdir(wikiconfig)
		return ConfigFile(ConfigFile.success, wikiconfig)
	except  FileExistsError:
		 return ConfigFile(ConfigFile.file_exists, wikiconfig)