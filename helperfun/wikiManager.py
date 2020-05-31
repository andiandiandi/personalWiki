from . import sessionManager
from . import configManager
from . import databaseManager
import sublime
import imp
from random import randrange

imp.reload(sessionManager)
imp.reload(configManager)
imp.reload(databaseManager)


def initWikiProject(window):
	ConfigFile = configManager.parse_config(window)
	if  ConfigFile.state == configManager.ConfigFile.no_config:
		ConfigFile = configManager.create_config()
	if ConfigFile.state == configManager.ConfigFile.success:
		db = databaseManager.Db(ConfigFile.path)
		db.init()
		
		if db.has_connection():
			db.drop_table()
			db.create_table()
			db.insert(str(window.window_id),randrange(1000))
			db.insert(str(window.window_id),randrange(1000))
			db.sel()
			sessionManager.add_wiki(window,db,ConfigFile.path)
			return True
		else:
			return False
	#no project found
	else:
		return False


############## debug ###################
def debug():
	sessionManager.current_wiki().db.remove_entry()

############## cleanup #####################
def clean_up():
	sessionManager.clean_up()



