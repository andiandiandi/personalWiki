from router import sessionRouter

import bottle
from beaker.middleware import SessionMiddleware


########### SESSIONS ####################################

session_opts = {
	'session.type': 'cookie',
	'session.url': '127.0.0.1:9000',
	"session.validate_key": "some secret",
	'session.cookie_expires': True,
	'session.auto': True
}

########## APP #######################################
app = SessionMiddleware(bottle.app(), session_opts)


######### HOOK ########################################
@bottle.hook('before_request')
def setup_request():
	if bottle.request.urlparts.path == '/init':
		return
	else:
		try:
			beaker_session = bottle.request.environ['beaker.session']
		except:
			bottle.abort(401, "Failed beaker_session")

		print("cookies")
		for c in bottle.request.cookies:
			print(c)

		try:
			id = beaker_session['id']
		except:
			 bottle.abort(401, "no valid session")

########## API ###########################################

@bottle.post('/init')
def init():
	session = bottle.request.environ.get('beaker.session')
	try:
		id = session['id']
		return "already has id"
	except:
		pass

	response = sessionRouter.route(bottle.request,session)

	if response:
		
		return str(session['id'])

	else:
		response.keep_alive = False
		return "failure"

@bottle.get('/search')
def search():
	session = bottle.request.environ.get('beaker.session')
	return str(session["id"])

@bottle.get('/close')
def test():
	session = bottle.request.environ.get('beaker.session')
	sessionRouter.clear_session(session["id"])
	session.delete()
	return "closed"

######### RUN ################################

bottle.run(
	app=app,
	host='127.0.0.1',
	port=9000,
	debug=True,
	reloader=True
)

