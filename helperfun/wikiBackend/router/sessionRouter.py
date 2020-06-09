from .manager import wikiManager

def route(request,session):
	wikipath = request.forms.get('wikipath')
	success = wikiManager.initWikiProject(wikipath,session)
	return success

def print():
	wikiManager.debug()

def clear_session(id):
	wikiManager.clear_session(id)