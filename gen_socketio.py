import socketio

# standard Python
sio = socketio.Client()

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")
    
sio.connect('http://192.168.2.60:8080')

sio.emit('eyes', {'x': '0.5', 'y': '0.5'})