import socketio
import time

sio = socketio.Client()
sio2 = socketio.Client()
sio3 = socketio.Client()

def connect():
    print('connected')

def res1(data):
    print("sio1 got response:" + str(data))

def disconnect():
    print("I'm disconnected!")

def res2(data):
	 print("sio2 got response:" + str(data))


def res3(data):
	 print("sio3 got response:" + str(data))

sio.on("connect",connect)
sio.on("res",res1)
sio.on("disconnect",disconnect)

sio2.on("connect",connect)
sio2.on("res",res2)
sio2.on("disconnect",disconnect)

sio3.on("connect",connect)
sio3.on("res",res3)
sio3.on("disconnect",disconnect)

sio.connect('http://localhost:9000')
sio2.connect('http://localhost:9000')
sio3.connect('http://localhost:9000')

print(sio.sid)
print(sio2.sid)
print(sio3.sid)

sio3.emit("message","hi")

time.sleep(2)
sio.disconnect()
sio2.disconnect()
sio3.disconnect()
