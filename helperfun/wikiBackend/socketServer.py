from flask import Flask, render_template, request
from flask_socketio import SocketIO

from manager import wikiManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@socketio.on("connect")
def connect():
	wikiManager.initWikiProject(request.sid)

@socketio.on('disconnect')
def test_disconnect():
	wikiManager.removeWiki(request.sid)

@socketio.on('debug')
def handle_message(message):
	socketio.emit('debug', str(wikiManager.sessions_count()), room=request.sid)

if __name__ == '__main__':
	socketio.run(app, host="127.0.0.1", port=9000)