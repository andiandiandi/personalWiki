from . import sessionManager
from . import configManager


def initWikiProject(wikipath):
	ConfigFile = configManager.parse_config(wikipath)
	if  ConfigFile.state == configManager.ConfigFile.no_config:
		return "no_config"
	if ConfigFile.state == configManager.ConfigFile.success:
		wiki = sessionManager.Wiki(ConfigFile.path)
		wiki.initialize()
		
		if wiki.db.has_connection():
			wiki.db.build_model()
			sessionManager.add_wiki(wiki)
			return True
		else:
			return False
	#no project found
	else:
		return False


############## debug ###################
def debug():
	current_wiki = sessionManager.current_wiki()
	print(current_wiki.window.window_id)
	print(current_wiki.db.configpath)
	current_wiki.db.sel()
	

############## cleanup #####################
def clean_up():
	sessionManager.clean_up()



