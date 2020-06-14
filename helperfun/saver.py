import sublime
import sublime_plugin
import imp
import json

from . import sessionManager
from . import pathManager
from . import localApi

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)

def save(root_folder):
	Connection = sessionManager.connection(root_folder)
	print(Connection)
	json_project_structure = json.dumps(pathManager.path_to_dict(root_folder))
	Connection.send("initdb", json_project_structure)
	print(json_project_structure)

def debug(root_folder):
	json_project_structure = json.dumps(pathManager.path_to_dict(root_folder))
	print(json_project_structure)