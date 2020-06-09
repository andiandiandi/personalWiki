from . import sessionManager

def initWikiProject(wikipath,session):
	wiki = sessionManager.Wiki(wikipath,session)
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



############## debug ###################
def debug():
	print(len(sessionManager.wikis))
	for wiki in sessionManager.wikis:
		if sessionManager.wikis[wiki].session:
			print(sessionManager.wikis[wiki].session)
			print(sessionManager.wikis[wiki].session["id"])
	

############## cleanup #####################
def clean_up():
	pass

def clear_session(id):
	for wiki in sessionManager.wikis:
		if sessionManager.wikis[wiki].session["id"] == id:
			 sessionManager.wikis[wiki].session=None
			 print("hit")
	


