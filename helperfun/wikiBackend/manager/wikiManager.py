from . import sessionManager

def initWikiProject(sid):
	wiki = sessionManager.Wiki(sid)
	sessionManager.add_wiki(wiki)
	#wiki.initialize_db()

	#db = wiki.db
	return True
	if db.has_connection():
		sessionManager.add_wiki(wiki)
		db.build_model()

		return True
	else:
		return False

def removeWiki(sid):
	sessionManager.remove_wiki(None,sid=sid)

def iniDbProject(sid,json_project_structure):
	Wiki = sessionManager.wiki(sid)
	if Wiki:
		Wiki.initialize_db(json_project_structure)

def sessions_count():
	return len(sessionManager.wikis)

############## debug ###################
def debug():
	pass
	

############## cleanup #####################
def clean_up():
	pass

	


