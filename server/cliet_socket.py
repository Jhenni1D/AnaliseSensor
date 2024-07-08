import socketio

sio = socketio.Client()

@sio.event
def connect():
    sio.emit("ping")
    print('connection established')
    print('send to server ping')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.event
def pong():
    print("receive pong")


sio.connect("http://127.0.0.1:8080/", wait_timeout=20)
sio.wait()