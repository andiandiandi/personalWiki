import os
from . import pathManager

__CONFIGFOLDERNAME = "wikiconfig"

class ConfigFile:
	success=0
	no_config=1

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
