import os
from . import pathManager

__CONFIGFOLDERNAME = "wikiconfig"

class ValidationResult:
	success=0
	no_project=1
	no_config=2

def validate():
	window_root = pathManager.root_folder_of_window()
	if not window_root:
		return ValidationResult.no_project

	wikiconfig = os.path.join(window_root,__CONFIGFOLDERNAME)
	config_exists = pathManager.exists(wikiconfig)
	if config_exists:
		return ValidationResult.success
	return ValidationResult.no_config

def create_config():
	window_root = pathManager.root_folder_of_window()
	if not window_root:
		return False
	wikiconfig = os.path.join(window_root,__CONFIGFOLDERNAME)
	try:
		os.mkdir(wikiconfig)
		return True
	except  FileExistsError:
		 return False
