import os
from . import pathManager

__CONFIGFOLDERNAME = "wikiconfig"

class ValidationResult:
	success=0
	failure=1
	no_project=2
	no_config=3

def validate():
	window_root = pathManager.root_folder_of_window()
	if not window_root:
		return ValidationResult.no_project, None

	wikiconfig = os.path.join(window_root,__CONFIGFOLDERNAME)
	config_exists = pathManager.exists(wikiconfig)
	if config_exists:
		return ValidationResult.success, wikiconfig
	return ValidationResult.no_config , None

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