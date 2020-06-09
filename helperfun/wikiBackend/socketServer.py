from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = []

@socketio.on("connect")
def connect():
	print("connected")
	clients.append(request.sid)

@socketio.on('disconnect')
def test_disconnect():
	print('Client disconnected')

@socketio.on('message')
def handle_message(message):
	socketio.emit('res', "received message " + str(request.sid), room=clients[1])

if __name__ == '__main__':
	socketio.run(app, host="127.0.0.1", port=9000)